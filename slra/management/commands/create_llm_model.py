from django.core.management.base import BaseCommand, CommandError
from slra.models import LLMModel, LLMProvider

class Command(BaseCommand):
    help = "Creates a new LLMModel record, linked to an existing LLMProvider."

    def add_arguments(self, parser):
        parser.add_argument('--provider-id', type=int, required=True, help='ID of the LLMProvider to link this model.')
        parser.add_argument('--model-name', type=str, required=True, help='Model name, e.g. "deepseek-r1".')
        # renamed argument from "--version" to "--model-version"
        parser.add_argument('--model-version', type=str, required=False, default='', help='Version tag if applicable.')
        parser.add_argument('--usage-method', type=str, required=False, default='', help='Usage method, e.g. "API call", "local Docker" etc.')
        parser.add_argument('--credentials', type=str, required=False, default='', help='Credentials if needed. (Store securely!)')
        parser.add_argument('--usage-instructions', type=str, required=False, default='', help='Docs or notes for using this model.')

    def handle(self, *args, **options):
        provider_id = options['provider_id']
        model_name = options['model_name'].strip()
        # retrieve the value from --model-version
        version_value = options['model_version'].strip()
        usage_method = options['usage_method'].strip()
        credentials = options['credentials'].strip()
        usage_instructions = options['usage_instructions'].strip()

        # Check provider
        try:
            provider = LLMProvider.objects.get(pk=provider_id)
        except LLMProvider.DoesNotExist:
            raise CommandError(f"No LLMProvider found with ID {provider_id}.")

        # Check if (provider, model_name, version) already exists
        if LLMModel.objects.filter(provider=provider, model_name=model_name, version=version_value).exists():
            raise CommandError(
                f"LLMModel '{model_name}' (version '{version_value}') already exists for provider '{provider.name}'."
            )

        llm_model = LLMModel.objects.create(
            provider=provider,
            model_name=model_name,
            version=version_value,
            usage_method=usage_method,
            credentials=credentials,
            usage_instructions=usage_instructions
        )
        self.stdout.write(self.style.SUCCESS(
            f"LLM Model '{llm_model.model_name}' (version: '{llm_model.version}') created under provider '{provider.name}' (ID: {llm_model.id})."
        ))
