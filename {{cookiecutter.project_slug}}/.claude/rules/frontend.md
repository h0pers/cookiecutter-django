---
paths:
  - "frontend/**"
  - "{{ cookiecutter.project_slug }}/templates/spa.html"
---

# Frontend (Vue 3 + Vite)

- Source lives in `frontend/src/`: `main.ts`, `App.vue`, `router/`, `stores/` (Pinia), `views/`, shadcn-vue components in `components/ui/`, helpers in `lib/`, styles in `assets/main.css`.
- Django serves `{{ cookiecutter.project_slug }}/templates/spa.html` for every URL under `/app/`; Vue Router (`createWebHistory('/app/')`) takes over from there. django-vite loads the dev server when `DEBUG` is on and the built files otherwise.
- Run commands from `frontend/`: `npm run dev`, `npm run build` (type-checks with `vue-tsc`, then builds into `{{ cookiecutter.project_slug }}/static/dist`), `npm run lint`, `npm run format`.
- UI components come from shadcn-vue (`frontend/components.json`). Use the `shadcn-vue` skill or the MCP server in `.mcp.json` to find and add them, and run the CLI from `frontend/` (`npx shadcn-vue@latest add <name>`). Don't hand-write a component the registry already provides, and don't edit `src/components/ui/` by hand; ESLint skips it because the CLI generates it.
- `.claude/skills/shadcn-vue/` is vendored from the shadcn-vue repository (`skills/shadcn-vue` at commit `0bfec13a`); update it by copying a newer version from there.
- Talk to Django through its API under `/api/`; don't duplicate business rules in the frontend.
- Add packages with `npm install <pkg>` from `frontend/`; never edit `package-lock.json` by hand.
- Run `npm run lint`, `npm run format` and `npm run build` before finishing a frontend change.
