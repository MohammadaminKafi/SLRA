from django.core.management.base import BaseCommand
from slra.models import SystematicReview, HypothesisKeyword

class Command(BaseCommand):
    help = "Lists all keywords for a given Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='ID of the Systematic Review')

    def handle(self, *args, **options):
        review_id = options['review_id']
        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No review found with ID {review_id}."))
            return

        keywords = HypothesisKeyword.objects.filter(systematic_review=review)
        if not keywords:
            self.stdout.write(self.style.WARNING(f"No keywords for '{review.name}'."))
            return

        self.stdout.write(self.style.SUCCESS(f"Keywords for '{review.name}':"))
        for k in keywords:
            self.stdout.write(f" - {k.keyword}")
