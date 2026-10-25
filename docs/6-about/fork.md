# About this fork

This fork of [cookiecutter-django](https://github.com/cookiecutter/cookiecutter-django) is a starting point for Django + Vue apps that share one VPS. It adds the following options on top of upstream:

- `frontend_pipeline = "Vite + Vue"`: a Vue 3 + TypeScript frontend built with Vite
- `use_external_traefik`: route through a shared Traefik instead of one Traefik per project
- `deploy_ssh`: build images in GitHub Actions, push them to GHCR and deploy to the VPS over SSH, with rollback
- `postgres_backup`: WAL-G continuous backups with point-in-time restore (default) or upstream's `pg_dump` scripts
- `use_ai_agents`: `AGENTS.md`, Claude rules, skills and hooks in the generated project (default)

The VPS itself (Docker, the shared Traefik, the `traefik-public` network, deploy users) is set up by [vps-infra](https://github.com/h0pers/vps-infra).

## Rules for changes

- Put new behaviour behind an option and keep upstream's code paths intact. With `postgres_backup=pg_dump` and `use_ai_agents=n` and every other new option at its default, the fork must generate what upstream generates.
- Follow upstream's layout (`config/settings/`, `compose/{local,production}/`, apps under the project slug).
- Add every new option to `SUPPORTED_COMBINATIONS` in `tests/test_cookiecutter_generation.py`, and invalid combinations to `UNSUPPORTED_COMBINATIONS`.
- Use Conventional Commits.

## Merging upstream

Merge upstream about once a month. Most upstream commits are dependency bumps from bots, so conflicts are rare and small.

```bash
git fetch upstream
git checkout -b chore/merge-upstream
git merge upstream/main
uv run pytest -n auto tests
```

Upstream's bot workflows (changelog, contributors, issue manager, pre-commit autoupdate) only run when `github.repository_owner == 'cookiecutter'`, so they stay idle here. PyUp, which upstream uses to bump the generated project's requirements, isn't set up for the fork, so those bumps arrive with upstream merges.

To check that the fork still matches upstream:

```bash
uv run cookiecutter . --no-input -o /tmp/fork postgres_backup=pg_dump use_ai_agents=n
git worktree add /tmp/upstream-src upstream/main
uv run cookiecutter /tmp/upstream-src --no-input -o /tmp/upstream
diff -r /tmp/upstream/my_awesome_project /tmp/fork/my_awesome_project
git worktree remove /tmp/upstream-src
```

Only generated secrets and passwords should differ.
