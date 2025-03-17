from django.core.management.base import BaseCommand
from slra.models import LLMModel

class Command(BaseCommand):
    help = "Lists all available LLMModels with their providers."

    def handle(self, *args, **options):
        models = LLMModel.objects.select_related('provider').all()
        if not models.exists():
            self.stdout.write(self.style.WARNING("No LLMModels found."))
            return

        self.stdout.write(self.style.SUCCESS("Available LLM Models:"))
        for m in models:
            self.stdout.write(f" - ID {m.id}: {m.model_name} (Provider: {m.provider.name})")
