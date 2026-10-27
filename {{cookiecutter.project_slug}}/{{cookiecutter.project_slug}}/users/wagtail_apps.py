from wagtail.users.apps import WagtailUsersAppConfig


# Lives outside apps.py: a second AppConfig there would stop Django from picking
# UsersConfig automatically
class WagtailUsersConfig(WagtailUsersAppConfig):
    user_viewset = "{{ cookiecutter.project_slug }}.users.wagtail_admin.WagtailUserViewSet"
