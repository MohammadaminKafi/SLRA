from django.core.management.base import BaseCommand, CommandError
from slra.models import LLMModel, SystematicReview, LLMQueryLog
from slra.services.llm_integration import get_llm_response
from slra.services import exceptions

class Command(BaseCommand):
    help = "Sends a custom prompt to a chosen LLM and prints the response."

    def add_arguments(self, parser):
        parser.add_argument('--model-id', type=int, required=True, help='LLMModel ID')
        parser.add_argument('--review-id', type=int, required=False, help='Systematic Review ID for context')
        parser.add_argument('--prompt', type=str, required=True, help='Prompt text to send')

    def handle(self, *args, **options):
        model_id = options['model_id']
        review_id = options.get('review_id')
        prompt_text = options['prompt']

        try:
            llm_model = LLMModel.objects.select_related('provider').get(pk=model_id)
        except LLMModel.DoesNotExist:
            raise CommandError(f"No LLMModel found with ID {model_id}.")

        # If review_id is provided, link to that review
        review = None
        if review_id:
            from myapp.models import SystematicReview
            try:
                review = SystematicReview.objects.get(pk=review_id)
            except SystematicReview.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"No SystematicReview with ID {review_id}, proceeding without link."))

        try:
            response_text = get_llm_response(llm_model, prompt_text)
        except exceptions.LLMError as e:
            raise CommandError(f"LLM call failed: {e}")

        # Print the result
        self.stdout.write(self.style.SUCCESS("LLM Response:\n"))
        self.stdout.write(response_text)

        # Log the query
        phase = 1 if not review else 4  # Example: 1=Problem Formulation, 4=Query Definition, adapt as needed
        LLMQueryLog.objects.create(
            systematic_review=review,
            llm_model=llm_model,
            phase=phase,
            prompt_text=prompt_text,
            response_text=response_text
        )
        self.stdout.write(self.style.SUCCESS("Query logged in LLMQueryLog."))
