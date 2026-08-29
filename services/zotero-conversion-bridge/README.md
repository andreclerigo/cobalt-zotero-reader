# Cobalt Zotero Conversion Bridge

This optional service adds structured Docling conversion to Cobalt's **Zotero
Reader** app. The app's collections, metadata, abstracts, and Zotero indexed
text work without it by connecting directly to Zotero API v3.

The bridge exposes allowlisted collections from one Zotero user library,
converts PDF attachments already stored in Zotero, and never writes to Zotero
or follows publisher URLs. It is useful for readers who want headings, tables,
formulas, OCR, and figures and have access to an owner- or community-hosted
instance.

For a guided deployment, start with the GitHub Pages-ready
[self-hosting guide](../../docs/self-hosting.html). This README remains the
service's concise operational reference.

## Hosting model

This is a single-host, stateful-cache service, not a static site or a
horizontally scalable stateless API. Zotero remains the source of truth and the
bridge never writes to it, but the deployment persists normalized HTML and
figures, Caddy's TLS state, and Docling's downloaded model cache. Active jobs
and their queue are local to one bridge process; after a restart, a client can
retry a conversion safely, but multiple bridge replicas must not be run against
the same deployment without adding shared job coordination.

GitHub Pages cannot host this service: it can publish only static site files and
cannot run FastAPI, Docker, background conversions, or server-side secrets. Use
a small always-on Linux host or VM with Docker Compose. The pinned images support
both `linux/amd64` and `linux/arm64`, so a Raspberry Pi is possible only with a
64-bit operating system. Docling's CPU image and models are large and conversion
is compute- and memory-intensive; for a personal low-volume installation, prefer
a 64-bit Raspberry Pi 5 with 8 GiB RAM and an SSD, or use a VPS for simpler
public DNS, TLS, and availability. A synthetic conversion completed in a 2 GiB,
2-CPU development VM after lazy loading was enabled, but it ran close to that
memory ceiling and was slow; 2 GiB is not a recommended production target.
Slower hardware can still serve cached documents, but first conversion will
take longer.

The current authorization model is deliberately single-user: one Zotero user,
one Zotero key, one bridge bearer token, and an allowlist of that user's
collections. Do not give the token to unrelated users or present this instance
as a public multi-tenant service. A community service would need per-user
authentication, isolated Zotero credentials and cache namespaces, quotas, abuse
controls, and shared durable job coordination.

## Configure

Python 3.12 and all Python dependencies are locked in this directory. Create a
dedicated Zotero API key with read-only library and file access. Copy
`.env.example` to `.env` on the deployment host and set every blank value.
`ALLOWED_COLLECTION_KEYS` is a comma-separated allowlist. Generate the bridge
and Docling bearer keys independently, for example with `openssl rand -hex 32`;
use the same Docling key for `DOCLING_API_KEY` and
`DOCLING_SERVE_API_KEY`.

The Docling container is constrained to one API process and one local conversion
worker. It lazy-loads the one pipeline requested by the bridge, avoiding a
second warm-up pipeline and its peak memory cost. Its file-size and
conversion-time limits mirror `MAX_PDF_BYTES` and
`CONVERSION_TIMEOUT_SECONDS`; keep those values synchronized when overriding
them. The readiness check verifies the service and worker loop; the first real
conversion is the model-loading smoke test and will be slower than later jobs.

`ZOTERO_READER_CACHE_PATH` must be a directory on an encrypted host volume.
Create it before starting Compose, assign it to the container's fixed uid/gid
`10001:10001`, and set mode `0700`. The `.env` file contains secrets and must
never be committed.

Source PDFs exist only while a conversion runs. Normalized HTML and figures
expire 30 days after last access and are bounded by the 10 GiB cache quota. The
Zotero and internal Docling origins are fixed and validated at startup. Item
authorization is cached for five minutes to keep polling and figure loading
within Zotero's request budget. A user or allowlist change invalidates the
derived-version namespace; purge the persistent cache when changing users.
Document responses send `Cache-Control: no-transform` so HTTPS intermediaries
such as Cloudflare cannot inject browser-only email-obfuscation scripts into
the sanitized HTML consumed by the Kobo.

## Run

```sh
docker compose config
docker compose up --build -d
docker compose ps
curl --fail https://papers.example.com/v1/health
```

Replace `papers.example.com` with the exact host written in `.env`.

If a non-default environment file is used, pass it to Compose as well as naming
it for the bridge, so interpolation values such as the Docling key and resource
limits come from the same file:

```sh
ZOTERO_BRIDGE_ENV_FILE=/absolute/path/bridge.env \
  docker compose --env-file /absolute/path/bridge.env up --build -d
```

Only Caddy publishes host ports. Docling is attached only to the internal
conversion network, Caddy discards access logs, and the bridge disables Uvicorn
access logs.

Compile the exact bare HTTPS origin into Cobalt and install the device-side
bridge token without putting it in source or a URL:

```sh
ZOTERO_READER_BRIDGE_ORIGIN=https://papers.example.com \
  cargo run -p kobo-cli -- package
kobo secret set zotero-bridge --device <address>
```

## Develop

```sh
uv sync --frozen --group dev
uv run ruff check .
uv run mypy src
uv run pytest
```

Tests use constructed Zotero responses and synthetic byte fixtures; they do not
need or read a real account. A live Docling smoke test is a deployment check,
not a substitute for the fixture suite.

Before directing a Kobo at the service, use a real allowlisted Zotero item with
a stored PDF to verify one complete upload, conversion, status poll, document
download, and figure download. This cannot be proven by the repository test
suite because it intentionally has no access to deployment secrets or private
library data.

## Failure and rollback

Expected conversion states use structured 2xx JSON so the Kobo can distinguish
`missing_pdf`, `queued`, `running`, `ready`, and `failed`. Authentication and
invalid paths fail closed. To roll back, revoke the bridge and Zotero keys, stop
the Compose project, and remove its volumes if the derived cache must be
destroyed. No Zotero restoration is necessary because the service is read-only.
The derived cache can be recreated from Zotero; retain `caddy_data` across normal
redeployments to preserve TLS state. The Docling model volume is also
reproducible, but deleting it makes the next start slower while models are
restored.
