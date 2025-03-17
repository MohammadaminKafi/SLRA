from django.core.management.base import BaseCommand, CommandError
from slra.models import LLMQueryLog

class Command(BaseCommand):
    help = "Deletes an LLM Query Log by ID."

    def add_arguments(self, parser):
        parser.add_argument('query_id', type=int, help='ID of the LLM Query Log')

    def handle(self, *args, **options):
        query_id = options['query_id']
        try:
            llm_query = LLMQueryLog.objects.get(pk=query_id)
        except LLMQueryLog.DoesNotExist:
            raise CommandError(f"No LLMQueryLog found with ID {query_id}.")

        llm_query.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted LLM Query Log ID {query_id} successfully."
        ))
