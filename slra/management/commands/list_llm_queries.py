from django.core.management.base import BaseCommand
from slra.models import LLMQueryLog, SystematicReview

class Command(BaseCommand):
    help = "Lists LLM Query Logs, optionally filtered by Systematic Review ID."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=False, help='Systematic Review ID to filter')

    def handle(self, *args, **options):
        review_id = options.get('review_id')

        if review_id:
            try:
                review = SystematicReview.objects.get(pk=review_id)
            except SystematicReview.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No review with ID {review_id}. Showing all queries instead."))
                review = None
        else:
            review = None

        if review:
            queries = LLMQueryLog.objects.filter(systematic_review=review)
            self.stdout.write(self.style.SUCCESS(f"LLM Queries for review '{review.name}':"))
        else:
            queries = LLMQueryLog.objects.all()
            self.stdout.write(self.style.SUCCESS("All LLM Queries:"))

        if not queries.exists():
            self.stdout.write(self.style.WARNING("No LLM Query Logs found."))
            return

        for q in queries:
            self.stdout.write(f" - ID {q.id}, Model: {q.llm_model}, Phase: {q.get_phase_display()}")
            self.stdout.write(f"   Prompt: {q.prompt_text[:60]}{'...' if len(q.prompt_text) > 60 else ''}")
