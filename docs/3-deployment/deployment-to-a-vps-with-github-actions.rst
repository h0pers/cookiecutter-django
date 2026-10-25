.. _deploy-ssh:

Deployment to a VPS with GitHub Actions
=======================================

.. index:: deployment, docker, github actions, ghcr, rollback

With ``deploy_ssh=y``, every push to ``main`` that passes CI is built, pushed to the GitHub Container Registry (GHCR) and deployed to your server without downtime. The option requires ``ci_tool=Github`` and ``use_external_traefik=y`` (see :ref:`shared-traefik`).

How it works
------------

``.github/workflows/build.yml`` runs when the ``CI`` workflow succeeds on a push to ``main``:

1. **build** pushes the production images to ``ghcr.io/<owner>/<repo>-<name>``. The names are ``django``, ``postgres``, ``nginx`` (``cloud_provider=None``) and ``awscli`` (``cloud_provider=AWS``). Each image is tagged ``sha-<full commit sha>`` and ``latest``, with the build cache kept under ``buildcache``.
2. **deploy** calls ``.github/workflows/deploy.yml`` with ``tag=sha-<sha>``.
3. **cleanup** keeps the 10 newest tagged versions of each image and deletes the rest. One of them is the build cache, so the images of the last 9 commits stay available for rollbacks.

``deploy.yml`` checks out the deployed commit and writes ``.envs/.production/.django`` and ``.envs/.production/.postgres`` from secrets. It also writes a ``.env`` that tells Docker Compose which images to use (``IMAGE_PREFIX`` and ``IMAGE_TAG``). It copies those files and ``docker-compose.production.yml`` to ``~/<repo>/`` on the server, then runs:

#. ``docker compose pull``
#. ``postgres``, ``redis``, ``nginx`` and ``postgres-backup`` are started if they aren't running. They aren't restarted on every deploy.
#. ``docker compose run --rm django /release`` runs migrations once. It also creates a superuser on the first deploy if ``DJANGO_SUPERUSER_PASSWORD`` is set.
#. ``docker rollout django`` starts a new ``django`` container. Once its healthcheck (``/healthz/``) passes, the old container fails its healthcheck on purpose, so Traefik stops routing to it, and it's then removed.
#. The Celery services restart on the new image.

``compose/production/django/start`` is unchanged: it runs in every container, so it shouldn't do one-off work such as migrations.

Server setup
------------

vps-infra_ prepares the server: Docker with the Compose plugin and docker-rollout_, the shared Traefik, and a deploy user in the ``docker`` group. Point your domain's DNS at the server (plus ``flower.<domain>`` if you use Celery).

GitHub settings
---------------

Create an environment called ``production`` (Settings → Environments) and add these secrets:

.. list-table::
   :header-rows: 1

   * - Secret
     - Value
   * - ``VPS_HOST``
     - Server hostname or IP
   * - ``VPS_USER``
     - Deploy user
   * - ``SSH_PRIVATE_KEY``
     - Private key whose public key is in the deploy user's ``authorized_keys``
   * - ``ENVS_PRODUCTION_DJANGO``
     - Full contents of ``.envs/.production/.django``. Add ``DJANGO_SUPERUSER_USERNAME``, ``DJANGO_SUPERUSER_EMAIL`` and ``DJANGO_SUPERUSER_PASSWORD`` to create the first superuser.
   * - ``ENVS_PRODUCTION_POSTGRES``
     - Full contents of ``.envs/.production/.postgres``
   * - ``ENVS_PRODUCTION_WALG``
     - Optional, with ``postgres_backup=WAL-G``: contents of ``.envs/.production/.walg`` to store backups in S3. The deploy fails if it sets ``WALG_S3_PREFIX`` without ``WALG_LIBSODIUM_KEY``.

The workflows log in to GHCR with the built-in ``GITHUB_TOKEN``, so no registry token is needed. Gunicorn's worker count comes from ``WEB_CONCURRENCY`` in ``.envs/.production/.django``.

Rolling back
------------

Run the **Deploy** workflow by hand (Actions → Deploy → Run workflow) with the tag to go back to, e.g. ``sha-<commit sha>``. The tags still available are listed on the repository's Packages page. The workflow deploys that commit's compose file with its images.

.. warning:: Rollbacks don't reverse migrations. If the newer release changed the database schema, make sure the older code still works with it, or reverse the migration by hand first.

Changing postgres, redis or nginx
---------------------------------

Deploys don't restart these services. After changing one of them, apply the change on the server:

.. code-block:: bash

    cd ~/<repo>
    docker compose -f docker-compose.production.yml up -d postgres

.. _vps-infra: https://github.com/h0pers/vps-infra
.. _docker-rollout: https://github.com/wowu/docker-rollout
