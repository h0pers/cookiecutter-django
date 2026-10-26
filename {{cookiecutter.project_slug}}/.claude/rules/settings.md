---
paths:
  - "config/settings/**"
  - ".envs/**"
---

# Settings

- `config/settings/base.py` holds everything shared; `local.py`, `test.py` and `production.py` start with `from .base import *` and override what differs. Put a setting in `base.py` unless it really is environment-specific.
- Read environment variables with django-environ's `env` (`env.str`, `env.bool`, `env.list`, `env.db`). Give a `default=` unless production must set the value, so local and test keep working.
- Development values go in `.envs/.local/`. `.envs/.production/` holds production secrets: never edit it; tell the user which variable to add and what it does.
- Settings for a new third-party package go in `base.py` under their own `# <package>` header with a link to its docs, like the existing sections.
- Never put real secrets in settings files.
