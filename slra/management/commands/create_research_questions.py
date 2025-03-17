from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, ResearchQuestion, LLMQueryLog, LLMModel
from slra.services.llm_integration import get_llm_response
from slra.services import exceptions

class Command(BaseCommand):
    help = "Generates Research Questions for a Systematic Review using an LLM."

    def handle(self, *args, **options):
        # Select a review
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

        # Select an LLM model
        llm_models = LLMModel.objects.all()
        if not llm_models.exists():
            self.stdout.write(self.style.ERROR("No LLMModel found. Create one first in the admin."))
            return

        self.stdout.write("Available LLM Models:")
        for idx, m in enumerate(llm_models, start=1):
            self.stdout.write(f"{idx}. {m} (Provider: {m.provider.name})")

        model_choice = input("Select an LLM Model by number: ")
        try:
            model_choice = int(model_choice.strip())
            selected_model = llm_models[model_choice - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR("Invalid choice. Aborting."))
            return

        # Ask for topic
        base_topic = input("Enter a topic or base question: ").strip()
        if not base_topic:
            self.stdout.write(self.style.ERROR("No topic given. Aborting."))
            return

        final_prompt = f"""You are an expert in research. Based on the topic below,
please generate 10 possible research questions.

Topic: {base_topic}

Questions:
"""

        self.stdout.write("Generating questions via LLM, please wait...")

        try:
            response_text = get_llm_response(selected_model, final_prompt)
        except exceptions.LLMError as e:
            self.stdout.write(self.style.ERROR(f"LLM call failed: {e}"))
            return

        # Simple parsing - each line might be a question
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]

        # Log this LLM call
        query_log = LLMQueryLog.objects.create(
            systematic_review=selected_review,
            llm_model=selected_model,
            phase=1,
            prompt_text=final_prompt,
            response_text=response_text
        )

        # Save as new ResearchQuestion records
        created_count = 0
        for line in lines:
            if line:
                ResearchQuestion.objects.create(
                    systematic_review=selected_review,
                    question_text=line
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_count} new ResearchQuestion(s) in '{selected_review.name}'."
        ))
