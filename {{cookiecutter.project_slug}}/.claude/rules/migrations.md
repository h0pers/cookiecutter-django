---
paths:
  - "{{ cookiecutter.project_slug }}/**/migrations/**"
---

# Migrations

- Generate migrations with `makemigrations <app>`; don't write schema migrations by hand.
- Never edit or delete a migration that is already committed (a hook blocks it). Fix mistakes with a new migration.
- A migration you just generated and haven't committed may be deleted and regenerated.
- Data migrations: `RunPython` with a reverse function (`migrations.RunPython.noop` if there's nothing to undo), using `apps.get_model(...)`, never direct model imports.
- Run `makemigrations --check` before finishing; it fails when models changed without a migration.
- Ruff skips migrations; don't reformat them.
