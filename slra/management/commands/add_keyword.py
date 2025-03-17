from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, HypothesisKeyword

class Command(BaseCommand):
    help = "Adds a keyword to a specific Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='ID of the Systematic Review')
        parser.add_argument('--keyword', type=str, required=True, help='Keyword to add')

    def handle(self, *args, **options):
        review_id = options['review_id']
        keyword = options['keyword'].strip()

        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            raise CommandError(f"Systematic Review with ID {review_id} not found.")

        # Create new keyword
        hk = HypothesisKeyword.objects.create(systematic_review=review, keyword=keyword)
        self.stdout.write(self.style.SUCCESS(
            f"Keyword '{keyword}' added to '{review.name}' (ID {review.id})."
        ))
