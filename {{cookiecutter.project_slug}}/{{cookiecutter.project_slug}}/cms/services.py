from django.db import transaction
from wagtail.models import Page
from wagtail.models import Site

from .models import HomePage


class HomePageService:
    @staticmethod
    @transaction.atomic
    def get_or_create_default(*, site_name: str = "") -> tuple[HomePage, bool]:
        """Make sure a HomePage exists and the default Site serves it.

        Safe to run repeatedly: an existing HomePage and Site are reused.
        """
        created = False
        home = HomePage.objects.first()
        if home is None:
            # wagtailcore's placeholder "Welcome" page takes the "home" slug; its
            # Site goes with it (on_delete=CASCADE)
            Page.objects.filter(depth=2, slug="home").exact_type(Page).delete()
            root = Page.get_first_root_node()
            home = root.add_child(instance=HomePage(title="Home", slug="home"))
            created = True

        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            Site.objects.create(
                hostname="localhost",
                root_page=home,
                is_default_site=True,
                site_name=site_name,
            )
        elif site.root_page_id != home.pk:
            site.root_page = home
            site.save(update_fields=["root_page"])
        return home, created
