from django.core.management.base import BaseCommand
from slra.models import SystematicReview, ResearchQuestion

class Command(BaseCommand):
    help = "Lists research questions for a given Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='Systematic Review ID')

    def handle(self, *args, **options):
        review_id = options['review_id']
        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No review with ID {review_id}."))
            return

        questions = ResearchQuestion.objects.filter(systematic_review=review)
        if not questions.exists():
            self.stdout.write(self.style.WARNING(f"No Research Questions for review '{review.name}'."))
            return

        self.stdout.write(self.style.SUCCESS(f"Research Questions for '{review.name}':"))
        for q in questions:
            self.stdout.write(f" - ID {q.id}: {q.question_text}")
