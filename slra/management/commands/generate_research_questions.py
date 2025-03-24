from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, ResearchQuestion, LLMQueryLog, LLMModel
from slra.services.llm_integration import get_llm_response
from slra.services import exceptions


class Command(BaseCommand):
    help = "Generates Research Questions for a Systematic Review using an LLM, with detailed user options."

    def handle(self, *args, **options):
        # -------------------------
        # 1) Select a Systematic Review
        # -------------------------
        reviews = SystematicReview.objects.all()
        if not reviews.exists():
            self.stdout.write(self.style.ERROR("No SystematicReview found. Create one first."))
            return

        self.stdout.write("Available Systematic Reviews:")
        for idx, r in enumerate(reviews, start=1):
            self.stdout.write(f"{idx}. {r.name} (ID: {r.id})")

        review_choice = input("Select a Systematic Review by number: ")
        try:
            review_choice = int(review_choice.strip())
            selected_review = reviews[review_choice - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR("Invalid choice. Aborting."))
            return

        # -------------------------
        # 2) Select an LLM Model
        # -------------------------
        llm_models = LLMModel.objects.all()
        if not llm_models.exists():
            self.stdout.write(self.style.ERROR(
                "No LLMModel found. Create one first in the admin or via command line."
            ))
            return

        self.stdout.write("\nAvailable LLM Models:")
        for idx, m in enumerate(llm_models, start=1):
            self.stdout.write(f"{idx}. {m} (Provider: {m.provider.name})")

        model_choice = input("Select an LLM Model by number: ")
        try:
            model_choice = int(model_choice.strip())
            selected_model = llm_models[model_choice - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR("Invalid choice. Aborting."))
            return

        # -------------------------
        # 3) Ask for the base topic
        # -------------------------
        base_topic = input("\nEnter a topic or base question: ").strip()
        if not base_topic:
            self.stdout.write(self.style.ERROR("No topic given. Aborting."))
            return

        # -------------------------
        # 4) Ask for the number of questions (default = 10)
        # -------------------------
        default_num_questions = 10
        user_input_num = input(f"How many questions should be generated? [Press Enter for {default_num_questions}]: ")
        try:
            num_questions = int(user_input_num) if user_input_num.strip() else default_num_questions
        except ValueError:
            num_questions = default_num_questions

        # -------------------------
        # 5) Construct the Prompt
        # -------------------------
        # We include an example to guide the LLM's style. 
        # We ask the LLM to enumerate the questions with `--1--`, `--2--`, etc.
        example_questions = """
--1-- How do researchers design and conduct AI-related studies in RSE, and what research methods are most commonly used?
--2-- What ethical issues do researchers face when developing AI software, and how are concerns like bias, explainability, and fairness addressed in RSE practices?
--3-- How does funding and institutional support influence the development, sustainability, and ethical alignment of AI research software in RSE?
--4-- What are the common software development practices in AI research within RSE, particularly regarding data management, sustainability, and the use of machine learning tools?
--5-- How are the FAIR principles (Findable, Accessible, Interoperable, Reusable) implemented in AI-related research software, and what challenges do researchers face in achieving compliance?
--6-- How do Research Software Engineers (RSEs) make decisions regarding the trade-offs between model performance, interpretability, and ethical considerations in AI development?
--7-- What are the key challenges and best practices in integrating AI technologies into existing research software infrastructures within different scientific domains?
--8-- What strategies are employed to manage and mitigate the environmental impact of AI research software, particularly concerning energy consumption and carbon footprint?
        """.strip()

        # We'll instruct the LLM to produce a set of N questions, each prefixed by `--1--`, `--2--`, etc.
        final_prompt = f"""You are an expert in research. 
Below is an example of the style we would like for the questions:
--------------------
{example_questions}
--------------------

Now, please generate {num_questions} possible research questions based on the following topic:
"{base_topic}"

Use the following format exactly:
--1-- <Question #1>
--2-- <Question #2>
... 
(Up to --{num_questions}--)

Only output the questions in that format, do not provide extra commentary.
"""

        self.stdout.write("\nGenerating questions via LLM, please wait...\n")

        # -------------------------
        # 6) Call the LLM
        # -------------------------
        try:
            response_text = get_llm_response(selected_model, final_prompt)
        except exceptions.LLMError as e:
            self.stdout.write(self.style.ERROR(f"LLM call failed: {e}"))
            return

        # -------------------------
        # 7) Parse the LLM output
        # -------------------------
        # We want to split by lines that start with `--<number>--`
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        parsed_questions = []
        current_question_parts = []

        for line in lines:
            if line.startswith("--") and line.count("--") >= 2:
                # new question start
                if current_question_parts:
                    parsed_questions.append(" ".join(current_question_parts).strip())
                    current_question_parts = []
                # remove the leading format, e.g., "--1-- "
                # we could do something like:
                splitted = line.split('--')
                # splitted might be ['', '1', '', ' question text'] depending on how it's structured
                # let's just strip from the start
                question_text = line
                question_text = question_text.replace('--', '', 2).strip()
                # e.g. turned from "--1-- question text" into "question text"
                current_question_parts.append(question_text)
            else:
                # continuation of the current question
                current_question_parts.append(line)

        # append last question if any
        if current_question_parts:
            parsed_questions.append(" ".join(current_question_parts).strip())

        # remove empty or whitespace questions
        parsed_questions = [q for q in parsed_questions if q.strip()]

        if not parsed_questions:
            self.stdout.write(self.style.WARNING(
                "No questions could be parsed from the LLM response. Please check the LLM's output format."
            ))
            return

        # -------------------------
        # 8) Show the questions to the user & let them choose which to keep
        # -------------------------
        self.stdout.write(self.style.SUCCESS("Generated Questions:\n"))
        for idx, qtext in enumerate(parsed_questions, start=1):
            self.stdout.write(f"{idx}. {qtext}")

        self.stdout.write("\nWhich questions should be added to the project? (Separate multiple with commas)")
        self.stdout.write("Example: 1,2,4 would keep Q#1, Q#2, Q#4 and discard the others.\n")
        keep_str = input("Enter your choices: ").strip()

        # If user enters nothing, we assume they want to discard all
        if not keep_str:
            self.stdout.write(self.style.WARNING("No questions selected. None will be saved."))
            # Log the query, but 0 questions get saved
            LLMQueryLog.objects.create(
                systematic_review=selected_review,
                llm_model=selected_model,
                phase=1,
                prompt_text=final_prompt,
                response_text=response_text
            )
            return

        # Parse choices
        keep_indices = []
        for part in keep_str.split(','):
            part = part.strip()
            try:
                idx_val = int(part)
                if idx_val < 1 or idx_val > len(parsed_questions):
                    raise ValueError
                keep_indices.append(idx_val)
            except ValueError:
                self.stdout.write(self.style.WARNING(f"Invalid selection: '{part}'. Ignoring."))

        # Deduplicate and sort
        keep_indices = sorted(set(keep_indices))

        # -------------------------
        # 9) Log this LLM call
        # -------------------------
        # We'll log the entire response regardless of what the user keeps
        query_log = LLMQueryLog.objects.create(
            systematic_review=selected_review,
            llm_model=selected_model,
            phase=1,
            prompt_text=final_prompt,
            response_text=response_text
        )

        # -------------------------
        # 10) Save only the chosen questions
        # -------------------------
        created_count = 0
        for i in keep_indices:
            question_text = parsed_questions[i - 1]
            ResearchQuestion.objects.create(
                systematic_review=selected_review,
                question_text=question_text
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nSaved {created_count} new ResearchQuestion(s) to '{selected_review.name}'."
        ))