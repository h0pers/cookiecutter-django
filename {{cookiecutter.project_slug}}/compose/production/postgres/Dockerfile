FROM docker.io/postgres:{{ cookiecutter.postgresql_version }}

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
{%- if cookiecutter.postgres_backup == 'WAL-G' %}

# Set by Docker: amd64 or arm64
ARG TARGETARCH
# https://github.com/wal-g/wal-g/releases
ARG WALG_VERSION=v3.0.9
# https://github.com/aptible/supercronic/releases
ARG SUPERCRONIC_VERSION=v0.2.51

# WAL-G needs CA certificates to reach S3 over HTTPS
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# WAL-G calls its arm64 build "aarch64", and publishes a checksum next to each archive
RUN case "$TARGETARCH" in amd64) arch=amd64 ;; arm64) arch=aarch64 ;; esac \
    && asset="wal-g-pg-24.04-$arch" \
    && cd /tmp \
    && curl -fsSLO "https://github.com/wal-g/wal-g/releases/download/$WALG_VERSION/$asset.tar.gz" \
    && curl -fsSLO "https://github.com/wal-g/wal-g/releases/download/$WALG_VERSION/$asset.tar.gz.sha256" \
    && sha256sum -c "$asset.tar.gz.sha256" \
    && tar -xzf "$asset.tar.gz" \
    && mv "$asset" /usr/local/bin/wal-g \
    && rm "$asset.tar.gz" "$asset.tar.gz.sha256" \
    && wal-g --version

# supercronic runs the backup schedule without a cron daemon; the checksums are the release asset digests
RUN case "$TARGETARCH" in \
        amd64) sha256=cc232108374e8e2b537045f2d5eaa1229f619db314c3ba6a14d38b35dc0aa123 ;; \
        arm64) sha256=4ae22576a78223d8ccdf5f3b3660a5cbb5288416bf0ca96afc4a36d195932b94 ;; \
    esac \
    && curl -fsSL -o /usr/local/bin/supercronic \
        "https://github.com/aptible/supercronic/releases/download/$SUPERCRONIC_VERSION/supercronic-linux-$TARGETARCH" \
    && echo "$sha256  /usr/local/bin/supercronic" | sha256sum -c - \
    && chmod +x /usr/local/bin/supercronic

# WAL-G storage when no S3 prefix is set, and the target for restores; only postgres can read them
RUN install -d -m 700 -o postgres -g postgres /walg /restore
ENV WALG_FILE_PREFIX=/walg \
    WALG_COMPRESSION_METHOD=zstd

COPY ./compose/production/postgres/walg/crontab /etc/supercronic/crontab
COPY ./compose/production/postgres/walg/walg-* /usr/local/bin/
RUN chmod +x /usr/local/bin/walg-*
{%- endif %}
