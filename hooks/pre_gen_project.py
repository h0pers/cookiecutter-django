# ruff: noqa: PLR0133
import sys

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

# The content of this string is evaluated by Jinja, and plays an important role.
# It updates the cookiecutter context to trim leading and trailing spaces
# from domain/email values
"""
{{ cookiecutter.update({ "domain_name": cookiecutter.domain_name | trim }) }}
{{ cookiecutter.update({ "email": cookiecutter.email | trim }) }}
"""

project_slug = "{{ cookiecutter.project_slug }}"
if hasattr(project_slug, "isidentifier"):
    assert project_slug.isidentifier(), f"'{project_slug}' project slug is not a valid Python identifier."

assert project_slug == project_slug.lower(), f"'{project_slug}' project slug should be all lowercase"

assert "\\" not in "{{ cookiecutter.author_name }}", "Don't include backslashes in author name."

if "{{ cookiecutter.use_whitenoise }}".lower() == "n" and "{{ cookiecutter.cloud_provider }}" == "None":
    print("You should either use Whitenoise or select a Cloud Provider to serve static files")
    sys.exit(1)

if "{{ cookiecutter.mail_service }}" == "Amazon SES" and "{{ cookiecutter.cloud_provider }}" != "AWS":
    print("You should either use AWS or select a different Mail Service for sending emails.")
    sys.exit(1)

if "{{ cookiecutter.use_external_traefik }}".lower() == "y" and "{{ cookiecutter.use_docker }}".lower() == "n":
    print("An external Traefik routes Docker containers, so it requires use_docker=y.")
    sys.exit(1)

if "{{ cookiecutter.deploy_ssh }}".lower() == "y" and (
    "{{ cookiecutter.ci_tool }}" != "Github" or "{{ cookiecutter.use_external_traefik }}".lower() == "n"
):
    # Zero-downtime rollouts need a proxy that discovers containers, which the shared Traefik does
    print("deploy_ssh runs in GitHub Actions behind a shared Traefik: use ci_tool=Github and use_external_traefik=y.")
    sys.exit(1)
