from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview

class Command(BaseCommand):
    help = "Deletes a Systematic Review by ID."

    def add_arguments(self, parser):
        parser.add_argument('review_id', type=int, help='ID of the review to delete')

    def handle(self, *args, **options):
        review_id = options['review_id']
        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            raise CommandError(f"Systematic Review with ID {review_id} does not exist.")

        review_name = review.name
        review.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Systematic Review '{review_name}' (ID: {review_id}) has been deleted."
        ))
