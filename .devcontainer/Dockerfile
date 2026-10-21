# Entorno de desarrollo de AdopPlant.
#
# Se apoya en la imagen oficial de Dev Containers para Python 3.14 y le anade
# dos cosas que el proyecto necesita:
#
#   1. Cliente de PostgreSQL 18 (apt.postgresql.org), porque
#      sql/base_inicial.sql usa los comandos psql \restrict y \unrestrict, que
#      solo existen desde psql 18.
#   2. Node.js 22 (NodeSource) para las pruebas de la web con node:test
#      (tests/*.cjs).
#
# Se instalan aqui y no con "features" para que la imagen sea la misma tanto
# con Docker Compose como con la extension Dev Containers.
FROM mcr.microsoft.com/devcontainers/python:3.1.6-3.14-bookworm

ARG POSTGRES_CLIENT_MAJOR=18
ARG NODE_MAJOR=22

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
 && install -d /usr/share/postgresql-common/pgdg \
 && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
 && . /etc/os-release \
 && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list \
 && curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash - \
 && apt-get update \
 && apt-get install -y --no-install-recommends "postgresql-client-${POSTGRES_CLIENT_MAJOR}" nodejs \
 && rm -rf /var/lib/apt/lists/* \
 && npm cache clean --force
