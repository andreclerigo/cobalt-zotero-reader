# Contributor instructions

## Scope

This repository publishes the Zotero Reader application source and its
optional Zotero/Docling conversion bridge. The Kobo runtime and SDK remain in
the Cobalt host repository. Do not copy Cobalt platform code into this
repository unless an integration snapshot is explicitly requested.

## Safety and boundaries

- Never commit Zotero API keys, bridge tokens, device credentials, private
  library data, PDFs, cache contents, or .env files.
- The app is read-only with respect to Zotero. Do not add Scholar scraping,
  publisher authentication, Zotero writes, or background synchronization.
- The bridge accepts only stored Zotero PDFs and keeps source bytes temporary.
- Treat existing files and fixtures as user-owned; preserve unrelated changes.

## Sources of truth

Executable Rust and Python code, tests and synthetic fixtures, then
configuration, then this documentation. If those disagree, report the
discrepancy and resolve it explicitly.

## Workflow

Keep changes small and explain them in commits. The app and bridge have
separate validation paths. A change to credential routing, URL authorization,
redirect handling, persistence, or conversion boundaries requires focused
negative tests and independent review in the Cobalt integration.

## Validation

For the bridge, run:

~~~
cd services/zotero-conversion-bridge
uv sync --frozen --group dev
uv run ruff check .
uv run mypy src
uv run pytest
docker compose config
~~~

For the app, follow docs/INTEGRATION.md and run the Cobalt host tests there.
This repository alone is not a complete Cobalt workspace.

For the static documentation, run:

~~~
python3 scripts/validate_docs.py
~~~
