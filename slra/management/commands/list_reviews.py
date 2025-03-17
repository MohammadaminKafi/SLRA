from django.core.management.base import BaseCommand
from slra.models import SystematicReview

class Command(BaseCommand):
    help = "Lists all Systematic Reviews."

    def handle(self, *args, **options):
        reviews = SystematicReview.objects.all()
        if not reviews:
            self.stdout.write(self.style.WARNING("No SystematicReviews found."))
            return

        self.stdout.write(self.style.SUCCESS("Systematic Reviews:"))
        for r in reviews:
            self.stdout.write(f" - ID {r.id}: {r.name}")
