from typing import ClassVar

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels: ClassVar = [
        *Page.content_panels,
        FieldPanel("body"),
    ]

    # The site root: one per site, directly under Wagtail's tree root
    max_count = 1
    parent_page_types: ClassVar = ["wagtailcore.Page"]
