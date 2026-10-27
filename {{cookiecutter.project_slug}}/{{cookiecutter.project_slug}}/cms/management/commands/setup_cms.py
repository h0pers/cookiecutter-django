from django.conf import settings
from django.core.management.base import BaseCommand

from {{ cookiecutter.project_slug }}.cms.services import HomePageService


class Command(BaseCommand):
    help = (
        "Create the default CMS pages and point the default Site at the home page. "
        "Safe to run repeatedly."
    )

    def handle(self, *args, **options):
        home, created = HomePageService.get_or_create_default(
            site_name=settings.WAGTAIL_SITE_NAME,
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created home page {home.pk}."))
        else:
            self.stdout.write(f"Home page {home.pk} already exists.")
