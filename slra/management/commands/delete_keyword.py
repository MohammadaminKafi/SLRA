from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, HypothesisKeyword

class Command(BaseCommand):
    help = "Deletes a keyword from a Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--review-id', type=int, required=True, help='ID of the Systematic Review')
        parser.add_argument('--keyword', type=str, required=True, help='Keyword to delete')

    def handle(self, *args, **options):
        review_id = options['review_id']
        keyword = options['keyword']

        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            raise CommandError(f"Systematic Review with ID {review_id} not found.")

        qs = HypothesisKeyword.objects.filter(systematic_review=review, keyword=keyword)
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f"No such keyword '{keyword}' in '{review.name}'."))
            return

        qs.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted {count} occurrence(s) of keyword '{keyword}' from review '{review.name}'."
        ))
