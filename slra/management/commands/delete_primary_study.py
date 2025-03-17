from django.core.management.base import BaseCommand, CommandError
from slra.models import PrimaryStudy

class Command(BaseCommand):
    help = "Deletes a Primary Study by ID."

    def add_arguments(self, parser):
        parser.add_argument('study_id', type=int, help='ID of the Primary Study to delete')

    def handle(self, *args, **options):
        study_id = options['study_id']
        try:
            study = PrimaryStudy.objects.get(pk=study_id)
        except PrimaryStudy.DoesNotExist:
            raise CommandError(f"Primary Study with ID {study_id} does not exist.")

        title = study.title
        study.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted Primary Study (ID {study_id}): {title}"
        ))
