from django.core.management.base import BaseCommand
from slra.models import SystematicReview, PrimaryStudy

class Command(BaseCommand):
    help = "Lists Primary Studies for a given Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='Systematic Review ID')

    def handle(self, *args, **options):
        review_id = options['review_id']
        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No review with ID {review_id}."))
            return

        studies = PrimaryStudy.objects.filter(systematic_review=review)
        if not studies.exists():
            self.stdout.write(self.style.WARNING(f"No Primary Studies for '{review.name}'."))
            return

        self.stdout.write(self.style.SUCCESS(f"Primary Studies for '{review.name}':"))
        for s in studies:
            self.stdout.write(f" - ID {s.id}: {s.title[:60]}{'...' if len(s.title) > 60 else ''}")
