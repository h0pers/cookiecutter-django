# Wagtail's user forms require first_name and last_name; User replaces both with a
# single `name` field.
from django.contrib.auth import get_user_model
from wagtail.users.forms import UserCreationForm
from wagtail.users.forms import UserEditForm
from wagtail.users.views.users import UserViewSet

User = get_user_model()

USER_FIELDS = {User.USERNAME_FIELD, "email", "name", "is_superuser", "groups"}


class WagtailUserCreationForm(UserCreationForm):
    first_name = None
    last_name = None

    class Meta(UserCreationForm.Meta):
        fields = USER_FIELDS


class WagtailUserEditForm(UserEditForm):
    first_name = None
    last_name = None

    class Meta(UserEditForm.Meta):
        fields = USER_FIELDS | {"is_active"}


class WagtailUserViewSet(UserViewSet):
    def get_form_class(self, for_update=False):  # noqa: FBT002
        return WagtailUserEditForm if for_update else WagtailUserCreationForm
