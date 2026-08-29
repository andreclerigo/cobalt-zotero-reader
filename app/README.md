# Zotero Reader

Zotero Reader is a read-only Cobalt app for browsing a Zotero collection and
reading paper text on a Kobo. Google Scholar can remain an input through the
Zotero Connector; the app never accesses or scrapes Scholar.

Start with the [setup guide](../docs/setup.html), or read the
[project documentation](../docs/index.html) for the two reading modes,
privacy boundaries, self-hosting, and troubleshooting.

## Serverless core

The default build connects directly to `https://api.zotero.org` using Zotero
Web API v3. It reads collections, metadata, abstracts, stored-PDF attachment
records, and Zotero's indexed plain text. It makes no Zotero write requests.

Create a dedicated **read-only** Zotero API key and note the numeric user ID on
the same Zotero key-management page. Install the key without putting it in Git
or a shell argument:

```sh
kobo secret set zotero --device <address>
```

Enter the numeric user ID on first launch, then choose a collection. Use the
**Collections** folder in the feed header to switch later; each collection has
its own cached list. Direct mode retains text, position, and annotations
offline. Zotero's full-text API is plain text, so figures, tables, formulas,
OCR, and original PDF layout are not preserved in this mode.

## Optional conversion bridge

An owner or community host can provide richer Docling conversion by compiling
an exact bare HTTPS origin into Cobalt:

```sh
ZOTERO_READER_BRIDGE_ORIGIN=https://papers.example.com \
  cargo run -p kobo-cli -- package
```

Install that service's separate bearer token as `zotero-bridge`:

```sh
kobo secret set zotero-bridge --device <address>
```

The runtime independently binds `zotero` to the approved read routes on the
exact Zotero API origin and binds `zotero-bridge` to `/v1/` on the exact
compiled bridge origin. A bridge is optional; its absence does not prevent
metadata or indexed-text reading.

For host development:

```sh
cargo test -p kobo-zotero-reader
cargo test -p kobo-net
cargo run -p kobo-cli -- run --sim --app zotero-reader
```

The committed Zotero responses under `fixtures/` are synthetic and contain no
account data or credentials.

For the complete deployment checklist, see
[Self-host the conversion bridge](../docs/self-hosting.html).
