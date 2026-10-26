---
paths:
  - "{{ cookiecutter.project_slug }}/**/models.py"
  - "{{ cookiecutter.project_slug }}/**/admin.py"
---

# Models and admin

- A model holds fields, `Meta` and `__str__`. Set `Meta.ordering` whenever the order of results matters.
- Properties are fine for simple values computed from the model's own fields. Anything that queries other tables or writes goes in the app's service.
- No business logic in `save()`, managers or signals. Use signals only for decoupled side effects such as cache invalidation.
- Foreign keys to users use `settings.AUTH_USER_MODEL`; code uses `get_user_model()`.
- Set `related_name` on every `ForeignKey` / `ManyToManyField` so reverse lookups read well (`order.items`).
- After changing fields or `Meta`, run `makemigrations <app>` and commit the new migration with the model change.
- Admin: register with `@admin.register(Model)`; write `list_display` and similar lists one item per line with a trailing comma.
