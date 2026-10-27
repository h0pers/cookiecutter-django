---
paths:
  - "{{ cookiecutter.project_slug }}/cms/**"
  - "{{ cookiecutter.project_slug }}/templates/cms/**"
---

# Wagtail pages

- Page models live in `cms/models.py` and subclass `wagtail.models.Page`. Add fields to `content_panels` with `FieldPanel`; SEO and slug fields come from `Page`.
- Restrict the tree with `parent_page_types` and `subpage_types` on every page model. `HomePage` sits directly under the tree root and `max_count = 1`.
- Flexible content: `StreamField` with blocks defined in `cms/blocks.py`, not inline in the model.
- Each page model renders `templates/cms/<model_name>.html` (`HomePage` → `cms/home_page.html`), extending `base.html` and using `{% raw %}{% load wagtailcore_tags %}{% endraw %}` for `richtext` and `pageurl`.
- `get_context()` may query the page tree (`self.get_children().live().specific()`); data from other apps comes from that app's service.
- Page-tree writes (creating default pages, moving pages) go in `HomePageService` or a new `<Page>Service` in `cms/services.py`. Data migrations use historical models, as in `0002_create_homepage.py`, not services.
- After changing a page model, run `makemigrations cms`.
- Wagtail's user admin uses the forms in `users/wagtail_admin.py`, because `User` has `name` instead of `first_name` / `last_name`. New user fields that editors should set go in `USER_FIELDS` there.
- Tests: function-style, as everywhere else. `Page.can_create_at(parent)` checks tree rules; the `client` fixture renders pages by URL, because the migrated HomePage serves `/`.
