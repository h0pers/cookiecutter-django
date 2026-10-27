from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CmsConfig(AppConfig):
    name = "{{ cookiecutter.project_slug }}.cms"
    verbose_name = _("CMS")
