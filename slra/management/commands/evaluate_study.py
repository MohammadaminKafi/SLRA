from django.core.management.base import BaseCommand, CommandError
from slra.models import PrimaryStudy, RelevancyEvaluation

class Command(BaseCommand):
    help = "Sets relevancy of a Primary Study (H, M, L, X)."

    def add_arguments(self, parser):
        parser.add_argument('--study-id', type=int, required=True, help='ID of the Primary Study')
        parser.add_argument('--relevancy', type=str, required=True, help='H, M, L, or X')

    def handle(self, *args, **options):
        study_id = options['study_id']
        relevancy = options['relevancy'].upper()

        valid_choices = [c[0] for c in RelevancyEvaluation.RELEVANCY_CHOICES]
        if relevancy not in valid_choices:
            raise CommandError(f"Invalid relevancy '{relevancy}'. Must be one of {valid_choices}.")

        try:
            study = PrimaryStudy.objects.get(pk=study_id)
        except PrimaryStudy.DoesNotExist:
            raise CommandError(f"No PrimaryStudy found with ID {study_id}.")

        RelevancyEvaluation.objects.create(
            primary_study=study,
            evaluator="CLI User",
            relevancy=relevancy
        )

        # Update the main relevancy_level, if not 'X' (excluded)
        if relevancy == 'X':
            # Some logic to handle exclusions
            study.relevancy_level = 'N'  # or keep as is, depending on your approach
        else:
            study.relevancy_level = relevancy
        study.save()

        self.stdout.write(self.style.SUCCESS(
            f"Primary Study ID {study_id} marked as relevancy '{relevancy}'."
        ))
