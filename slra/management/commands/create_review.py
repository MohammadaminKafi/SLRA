from django.core.management.base import BaseCommand, CommandError
from slra.models import SystematicReview

class Command(BaseCommand):
    help = "Creates a new Systematic Review by providing a name."

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name for the new Systematic Review')

    def handle(self, *args, **options):
        name = options['name'].strip()

        if SystematicReview.objects.filter(name=name).exists():
            raise CommandError(f"A Systematic Review named '{name}' already exists.")

        review = SystematicReview.objects.create(name=name)
        self.stdout.write(self.style.SUCCESS(
            f"Systematic Review '{review.name}' created with ID {review.id}."
        ))
