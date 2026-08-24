# Development workflow

## Bridge checks

The bridge uses Python 3.12 and a locked uv.lock. From
services/zotero-conversion-bridge/:

~~~
uv sync --frozen --group dev
uv run ruff check .
uv run mypy src
uv run pytest
docker compose config
~~~

The tests use synthetic Zotero responses and byte fixtures. They do not need
or access a real account. A live conversion is a deployment check and must use
a staging collection and token first.

## App checks

The app must be copied into a Cobalt checkout before compiling. Run the narrow
package tests, simulator, formatting, and workspace checks described in
docs/INTEGRATION.md. A simulator run is not Elipsa 2E hardware evidence.

## Device workflow

Before an attended test:

1. Build from the Cobalt checkout with the exact bridge HTTPS origin.
2. Install the read-only Zotero credential and, if needed, the bridge token
   through kobo secret set.
3. Run the read-only doctor and a simulator scenario.
4. Deploy to an owner-attended Kobo, exercise refresh, metadata, conversion,
   reading position, annotation, Wi-Fi loss, bridge outage, app exit, and
   return to the stock reader.
5. Record device model, firmware, commands, and observed failures separately
   from simulator or fixture evidence.

Never publish device IP addresses, credentials, private paper content, or
bridge logs containing authorization material.
