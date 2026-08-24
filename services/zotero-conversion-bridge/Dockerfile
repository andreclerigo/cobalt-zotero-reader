FROM python:3.12.11-slim@sha256:47ae396f09c1303b8653019811a8498470603d7ffefc29cb07c88f1f8cb3d19f AS build

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.8.11@sha256:8101ad825250a114e7bef89eefaa73c31e34e10ffbe5aff01562740bac97553c /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.12.11-slim@sha256:47ae396f09c1303b8653019811a8498470603d7ffefc29cb07c88f1f8cb3d19f
RUN groupadd --system --gid 10001 bridge \
    && useradd --system --uid 10001 --gid bridge --home /app bridge
COPY --from=build --chown=bridge:bridge /app /app
WORKDIR /app
USER bridge
EXPOSE 8000
ENTRYPOINT ["/app/.venv/bin/uvicorn"]
CMD ["papers_bridge.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
