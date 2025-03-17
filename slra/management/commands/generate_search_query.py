from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, SearchQuery, LLMModel, LLMQueryLog
from slra.services.llm_integration import get_llm_response
from slra.services import exceptions

class Command(BaseCommand):
    help = "Generates a refined search query using an LLM for a given Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='Systematic Review ID')

    def handle(self, *args, **options):
        review_id = options['review_id']
        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            raise CommandError(f"No SystematicReview with ID {review_id}.")

        # Let user pick an LLM:
        llm_models = LLMModel.objects.all()
        if not llm_models.exists():
            raise CommandError("No LLMModel found. Create one first.")

        self.stdout.write("Available LLM Models:")
        for idx, m in enumerate(llm_models, start=1):
            self.stdout.write(f"{idx}. {m} (Provider: {m.provider.name})")

        model_choice = input("Select an LLM Model by number: ")
        try:
            model_choice = int(model_choice.strip())
            selected_model = llm_models[model_choice - 1]
        except (ValueError, IndexError):
            raise CommandError("Invalid choice. Aborting.")

        base_topic = input("Enter a base topic to refine into a search query: ").strip()
        if not base_topic:
            raise CommandError("No topic provided.")

        # Example prompt
        final_prompt = f"Please generate an advanced boolean search query for the topic: {base_topic}"

        try:
            response_text = get_llm_response(selected_model, final_prompt)
        except exceptions.LLMError as e:
            raise CommandError(f"LLM call failed: {e}")

        # Create a new SearchQuery
        sq = SearchQuery.objects.create(
            systematic_review=review,
            query_string=response_text
        )

        # Log query
        LLMQueryLog.objects.create(
            systematic_review=review,
            llm_model=selected_model,
            phase=4,  # Query String Definition
            prompt_text=final_prompt,
            response_text=response_text
        )

        self.stdout.write(self.style.SUCCESS(
            f"Created new SearchQuery (ID {sq.id}) for review '{review.name}'."
        ))
