FROM docker.io/node:26.5-bookworm-slim

{% if cookiecutter.frontend_pipeline == 'Vite + Vue' -%}
WORKDIR /app/frontend

COPY ./frontend/package.json ./frontend/package-lock.json ./

RUN npm ci && npm cache clean --force
{%- else -%}
WORKDIR /app

COPY ./package.json /app

RUN npm install && npm cache clean --force
{%- endif %}

ENV PATH=./node_modules/.bin/:$PATH
