import csv
from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview, PrimaryStudy

class Command(BaseCommand):
    help = "Imports primary studies from a CSV file into a specified Systematic Review."

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Path to CSV file')
        parser.add_argument('--review-id', type=int, required=True, help='Systematic Review ID')

    def handle(self, *args, **options):
        file_path = options['file']
        review_id = options['review_id']

        try:
            review = SystematicReview.objects.get(pk=review_id)
        except SystematicReview.DoesNotExist:
            raise CommandError(f"Systematic Review with ID {review_id} not found.")

        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                created_count = 0
                for row in reader:
                    title = row.get('title', '').strip()
                    if not title:
                        # skip blank lines
                        continue
                    ps = PrimaryStudy.objects.create(
                        systematic_review=review,
                        title=title,
                        url=row.get('url'),
                        abstract=row.get('abstract'),
                        publication_year=row.get('publication_year') or None,
                        citations=row.get('citations') or None
                    )
                    created_count += 1
        except FileNotFoundError:
            raise CommandError(f"File not found: {file_path}")

        self.stdout.write(self.style.SUCCESS(
            f"Imported {created_count} primary study/studies into review '{review.name}'."
        ))
