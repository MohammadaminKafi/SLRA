from django.core.management.base import BaseCommand, CommandError
from slra.models import ResearchQuestion

class Command(BaseCommand):
    help = "Deletes a Research Question by ID."

    def add_arguments(self, parser):
        parser.add_argument('question_id', type=int, help='ID of the Research Question to delete')

    def handle(self, *args, **options):
        question_id = options['question_id']
        try:
            rq = ResearchQuestion.objects.get(pk=question_id)
        except ResearchQuestion.DoesNotExist:
            raise CommandError(f"Research Question with ID {question_id} does not exist.")

        rq.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Research Question (ID {question_id}) deleted successfully."
        ))
