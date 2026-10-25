.. _vite-vue:

Vite + Vue
==========

.. index:: vite, vue, frontend

With ``frontend_pipeline`` set to ``Vite + Vue``, the project gets a Vue 3 + TypeScript app in ``frontend/``, built with Vite_ and loaded by Django through django-vite_.

What you get
------------

* Vue 3, Vue Router and Pinia, scaffolded with ``create-vue`` (TypeScript, ESLint with oxlint, Prettier)
* Tailwind CSS 4 and shadcn-vue_, with a ``Button`` component as an example
* ``spa.html``: the Django template that loads the app. Every URL under ``/app/`` renders it, and Vue Router takes over from there.

The rest of the site is unchanged: ``base.html`` and the allauth pages keep Bootstrap, the same as with ``None``. Tailwind's styles only load on ``/app/``, so they don't clash with Bootstrap.

Local development
-----------------

With Docker, the ``node`` service runs the Vite dev server on port 5173. Open the app through Django, at http://localhost:8000/app/. Django's tags point at the dev server, and edits under ``frontend/src`` show up without a reload.

The ``node`` service sets ``WATCH_POLLING=true`` because file change events don't reach containers with some Docker setups (for example Colima, or WSL2 with files on Windows). Polling uses CPU. If file events reach your containers, set it to ``'false'`` in ``docker-compose.local.yml``.

Without Docker, run the dev server next to Django:

.. code-block:: bash

    cd frontend
    npm install
    npm run dev

To load the built files instead of the dev server, for example to check a build, run ``npm run build`` and set ``DJANGO_VITE_DEV_MODE=False``.

Commands
--------

Run these in ``frontend/``:

* ``npm run lint``: oxlint and ESLint, with fixes
* ``npm run format``: Prettier
* ``npm run build``: type-checks with ``vue-tsc``, then builds into ``<project_slug>/static/dist``
* ``npx shadcn-vue@latest add <component>``: adds a component under ``src/components/ui``. ESLint skips that folder because the CLI generates it.

With ``ci_tool=Github``, a ``frontend`` CI job checks formatting, lints, type-checks and builds.

Production
----------

The production Dockerfile builds the app in a Node stage and copies only ``static/dist`` into the Python image, so production needs no Node. ``collectstatic`` collects the built files with the other static files.

The built files reference each other with relative URLs, so they work wherever ``STATIC_URL`` points: Whitenoise, or a cloud storage bucket. django-vite reads the build manifest from the build output directly, and the manifest isn't published.

.. _Vite: https://vite.dev
.. _django-vite: https://github.com/MrBin99/django-vite
.. _shadcn-vue: https://www.shadcn-vue.com
