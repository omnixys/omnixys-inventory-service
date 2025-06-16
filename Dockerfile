# syntax=docker/dockerfile:1.14.0

ARG PYTHON_MAIN_VERSION=3.13
ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}.2
ARG UV_VERSION=0.6.9

# ------------------------------------------------------------------------------
# 🧱 Stage 1: Builder
# ------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_MAIN_VERSION}-bookworm-slim AS builder
WORKDIR /opt/app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Install dependencies from lockfile (mounting for cache and consistency)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml <<EOF \
    uv venv
    uv sync --frozen --no-install-project --no-dev --no-editable
EOF

ADD . /opt/app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ------------------------------------------------------------------------------
# 🚀 Stage 2: Runtime
# ------------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim-bookworm AS final
WORKDIR /opt/app

ARG APP_NAME
ARG APP_VERSION
ARG CREATED
ARG REVISION
ARG PYTHON_MAIN_VERSION
ARG PYTHON_VERSION=${PYTHON_MAIN_VERSION}.2
ARG UV_VERSION=0.6.9

LABEL org.opencontainers.image.title="omnixys-${APP_NAME}-service" \
      org.opencontainers.image.description="Omnixys ${APP_NAME}-service – Python ${PYTHON_VERSION}, basiert auf Debian Bookworm, gebaut mit uv ${UV_VERSION}" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.licenses="GPL-3.0-or-later" \
      org.opencontainers.image.vendor="omnixys" \
      org.opencontainers.image.authors="caleb.gyamfi@omnixys.com" \
      org.opencontainers.image.base.name="python:${PYTHON_VERSION}-slim-bookworm" \
      org.opencontainers.image.url="https://github.com/omnixys/omnixys-${APP_NAME}-service" \
      org.opencontainers.image.source="https://github.com/omnixys/omnixys-${APP_NAME}-service" \
      org.opencontainers.image.created="${CREATED}" \
      org.opencontainers.image.revision="${REVISION}" \
      org.opencontainers.image.documentation="https://github.com/omnixys/omnixys-${APP_NAME}-service/blob/main/README.md"

RUN set -eux; \
    apt-get update; \
    apt-get install --no-install-recommends --yes wget; \
    apt-get autoremove -y; \
    apt-get clean -y; \
    rm -rf /var/lib/apt/lists/* /tmp/*; \
    groupadd --gid 10000 app; \
    useradd --uid 10000 --gid app --shell /bin/bash --no-create-home app; \
    chown -R app:app /opt/app

USER app
COPY --from=builder --chown=app:app /opt/app ./
ENV PATH="/opt/app/.venv/bin:$PATH"

EXPOSE 8000
STOPSIGNAL SIGINT

CMD ["python", "-m", "analytics"]
