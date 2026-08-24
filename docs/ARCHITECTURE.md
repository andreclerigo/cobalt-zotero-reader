# Architecture and boundaries

## Components

The Rust app is a managed Cobalt built-in. It uses the Cobalt SDK for
networking, named credentials, cached Store values, Shelf blobs, and
BookView. Its normal data source is one personal Zotero user library and a
user-selected collection.

The optional bridge is a single-host, stateful-cache FastAPI service. It
authenticates one Zotero read-only key and one bridge bearer token, checks
collection membership, downloads only stored PDF attachments, uploads bytes to
Docling, and serves bounded normalized HTML and figures over HTTPS.

## Trust boundaries

- Google Scholar is an input workflow through Zotero Connector, not an app
  endpoint.
- The Kobo app holds credential names, not credential values.
- Zotero is read-only. The bridge never follows item URLs or publisher links.
- Docling receives PDF bytes on an internal Compose network, never a public
  URL.
- Source PDFs are job-scoped temporary data. The persistent bridge cache holds
  derived HTML and figures with expiry and quota limits.

## Current non-goals

This snapshot does not provide group libraries, saved-search synchronization,
Zotero writes, Scholar scraping, citation graphs, recommendations, public
multi-tenant hosting, annotation synchronization, or public Store release.

## Compatibility boundary

The app is not a standalone Rust workspace. Its Cargo.toml intentionally uses
Cobalt workspace paths. Build and device validation must run from a Cobalt
checkout with the app registered as a workspace member and with the matching
credential-policy support.
