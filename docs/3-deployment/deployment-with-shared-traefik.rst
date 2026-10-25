.. _shared-traefik:

Deployment behind a shared Traefik
==================================

.. index:: deployment, docker, traefik

By default, ``docker-compose.production.yml`` starts its own Traefik, which binds ports 80 and 443. A second project on the same server can't bind them again. With ``use_external_traefik=y``, the project leaves that job to one Traefik that serves every project on the server.

What changes
------------

* There's no ``traefik`` service and no ``compose/production/traefik/`` directory.
* ``django`` joins the external ``traefik-public`` network and declares its routes with Docker labels:

  * ``Host(<domain_name>)`` on the ``websecure`` entrypoint, with certificates from the ``le`` resolver.
  * ``www.<domain_name>`` permanently redirects to ``<domain_name>``, when the domain has a single dot.
  * Middlewares that keep ``X-CSRFToken`` behind the proxy (the same as upstream's Traefik config) and remove the ``Server`` response header.

* ``nginx`` (when ``cloud_provider`` is ``None``) serves ``/media/`` with ``X-Content-Type-Options: nosniff``.
* ``flower`` (when ``use_celery`` is ``y``) is served on ``flower.<domain_name>``, not on port 5555, so it needs its own DNS record.
* ``celeryworker`` and ``celerybeat`` stay off ``traefik-public``.

Router, service and middleware names start with the project slug, so give projects on one server distinct slugs.

What the server needs
---------------------

The shared Traefik must provide:

* A Docker provider with ``exposedbydefault=false``
* An external network called ``traefik-public``
* Entrypoints ``web`` (redirecting to HTTPS) and ``websecure``
* A certificate resolver called ``le``

vps-infra_ sets all of this up.

Then deploy as described in :doc:`deployment-with-docker`, without the Traefik steps:

.. code-block:: bash

    docker compose -f docker-compose.production.yml up -d

.. _vps-infra: https://github.com/h0pers/vps-infra
