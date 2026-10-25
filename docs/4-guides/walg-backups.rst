.. _walg-backups:

PostgreSQL Backups with WAL-G
=============================

.. index:: backups, postgres, wal-g, point-in-time recovery

With ``postgres_backup=WAL-G`` (the default, with ``use_docker=y``), production PostgreSQL is backed up continuously with WAL-G_. You can restore the latest state or any moment in the past (point-in-time recovery).

* **WAL archiving:** ``postgres`` ships every finished WAL segment to WAL-G storage, and forces a new segment at least once a minute (``archive_timeout=60``). At most about a minute of writes is at risk.
* **Base backups:** the ``postgres-backup`` service takes one when it first starts and then nightly at 03:00 UTC. It keeps the last 4 full backups and the WAL needed to replay from them.

The pg_dump commands from :doc:`docker-postgres-backups` (``backup``, ``backups``, ``restore``, ``rmbackup``) still work for one-off logical dumps.

Where backups are stored
------------------------

By default, WAL-G writes to the ``production_postgres_walg`` volume on the same server. That protects you from mistakes such as a dropped table, but not from losing the server or its disk. WAL-G's docs say not to use it as a disaster recovery plan. For that, store backups in S3 or any S3-compatible storage by setting these in ``.envs/.production/.walg``:

.. code-block:: bash

    WALG_S3_PREFIX=s3://bucket/project
    AWS_ACCESS_KEY_ID=...
    AWS_SECRET_ACCESS_KEY=...
    AWS_REGION=...
    # For S3-compatible storage, e.g. Cloudflare R2 or Hetzner:
    AWS_ENDPOINT=https://...
    AWS_S3_FORCE_PATH_STYLE=true
    # Required with S3: backups are encrypted before upload. Generate with: openssl rand -hex 32
    WALG_LIBSODIUM_KEY=...
    WALG_LIBSODIUM_KEY_TRANSFORM=hex

``postgres-backup`` refuses to start when ``WALG_S3_PREFIX`` is set without ``WALG_LIBSODIUM_KEY``. Keep the key somewhere other than the server: without it, the backups can't be read. Restart both services after changing the file:

.. code-block:: bash

    docker compose -f docker-compose.production.yml up -d postgres postgres-backup

With ``deploy_ssh``, put the contents of this file in the optional ``ENVS_PRODUCTION_WALG`` secret instead. See :ref:`deploy-ssh`.

Checking backups
----------------

.. code-block:: bash

    # Base backups
    docker compose -f docker-compose.production.yml exec postgres-backup wal-g backup-list --detail
    # WAL archiving: failed_count should stay at 0
    docker compose -f docker-compose.production.yml exec postgres sh -c \
      'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM pg_stat_archiver"'
    # Take a base backup now
    docker compose -f docker-compose.production.yml exec postgres-backup walg-backup

If archiving fails, for example because of wrong S3 credentials, PostgreSQL keeps the WAL in ``pg_wal`` until it succeeds, and the disk fills up.

Restoring
---------

A restore goes into a new volume, so the current database stays untouched until you switch. The examples use ``myproject`` as the Compose project name (the directory name; see ``docker volume ls``), so the database volume is ``myproject_production_postgres_data``. Times are in UTC.

#. Stop everything that writes to the database:

   .. code-block:: bash

       docker compose -f docker-compose.production.yml stop django postgres-backup postgres

   Also stop ``celeryworker``, ``celerybeat`` and ``flower`` if you use Celery.

#. Restore into a new, empty volume, to the latest state or to a moment in the past. Relative times such as ``"10 minutes ago"`` also work:

   .. code-block:: bash

       docker volume create myproject_postgres_restored
       docker compose -f docker-compose.production.yml run --rm --no-deps \
         -v myproject_postgres_restored:/restore postgres-backup walg-restore "2026-10-02 14:25"

   The output ends with ``restored_up_to``: check that it's the moment you expect.

#. Switch to the restored data. Keep a copy of the current data first, then replace it:

   .. code-block:: bash

       docker volume create myproject_postgres_before_restore
       docker compose -f docker-compose.production.yml run --rm --no-deps --user root --entrypoint bash \
         -v myproject_postgres_before_restore:/before -v myproject_postgres_restored:/restore postgres-backup \
         -c 'cp -a "$PGDATA"/. /before/ && find "$PGDATA" -mindepth 1 -delete && cp -a /restore/. "$PGDATA"/'

#. Start the stack and take a base backup of the restored database:

   .. code-block:: bash

       docker compose -f docker-compose.production.yml up -d
       docker compose -f docker-compose.production.yml exec postgres-backup walg-backup

#. Once the site looks right, remove the extra volumes:

   .. code-block:: bash

       docker volume rm myproject_postgres_restored myproject_postgres_before_restore

.. warning:: Only restore when you're going to switch to the result. A restore starts a new timeline in WAL-G storage, and later restores follow the newest timeline. A restore you don't switch to would send later restores down that abandoned branch.

Upgrading PostgreSQL
--------------------

Base backups and WAL only work with the major version that wrote them. After a major upgrade, point WAL-G at a fresh location (a new ``WALG_S3_PREFIX``, or remove the ``production_postgres_walg`` volume) and take a base backup.

.. _WAL-G: https://github.com/wal-g/wal-g
