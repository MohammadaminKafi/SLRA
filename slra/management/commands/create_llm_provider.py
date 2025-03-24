from django.core.management.base import BaseCommand, CommandError
from slra.models import LLMProvider

class Command(BaseCommand):
    help = "Creates a new LLM Provider record (e.g., 'Ollama', 'together.ai', 'OpenAI')."

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='Name of the provider (unique).')
        parser.add_argument('--base-url', type=str, required=False, help='Base URL or endpoint for API calls.')
        parser.add_argument('--description', type=str, required=False, help='Optional description of the provider.')

    def handle(self, *args, **options):
        name = options['name'].strip()
        base_url = options.get('base_url')
        description = options.get('description', '')

        # Check if provider with this name already exists
        if LLMProvider.objects.filter(name=name).exists():
            raise CommandError(f"Provider '{name}' already exists. Please choose a different name.")

        provider = LLMProvider.objects.create(
            name=name,
            base_url=base_url,
            description=description
        )
        self.stdout.write(self.style.SUCCESS(
            f"LLM Provider '{provider.name}' created (ID: {provider.id})."
        ))
