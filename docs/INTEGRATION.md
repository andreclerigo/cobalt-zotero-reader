# Integrating with Cobalt

This repository intentionally contains the app and bridge, not a second copy
of the Cobalt runtime. The app package currently uses relative workspace
dependencies such as ../../crates/kobo-sdk, so it must be integrated into a
Cobalt checkout.

## Host checkout

Use a Cobalt checkout from the upstream project or your fork. For the current
development snapshot, the checkout also needs the operation-aware credential
support from Cobalt PR 50, or the equivalent merged platform revision.

From the root of the Cobalt checkout:

~~~
mkdir -p examples/zotero-reader
cp -R /path/to/cobalt-zotero-reader-public/app/. examples/zotero-reader/
~~~

Add examples/zotero-reader to the Cobalt workspace members and apply the
managed-built-in registration changes from the Cobalt development branch. The
platform policy, app registration, and app source are deliberately separate
review units; do not add this app to apps/catalog.json or the public Store
workflow yet.

## Host validation

From the Cobalt checkout:

~~~
cargo fmt --all -- --check
cargo test -p kobo-zotero-reader
cargo test -p kobo-net
cargo run -p kobo-cli -- run --sim --app zotero-reader
cargo test --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
~~~

The app uses direct Zotero reads by default. To exercise the optional
conversion path, compile with the exact bare HTTPS bridge origin:

~~~
ZOTERO_READER_BRIDGE_ORIGIN=https://papers.example.com \
  cargo run -p kobo-cli -- run --sim --app zotero-reader
~~~

The origin is compiled into the app and must be HTTPS with no path or
alternate port. Install secrets through the device credential store:

~~~
kobo secret set zotero --device <address>
kobo secret set zotero-bridge --device <address>
~~~

The second credential is needed only when the optional bridge is enabled.
Never replace <address> with a value in committed documentation.

## Deployment order

For a real test, start with a staging Zotero collection and bridge token:

1. Run the bridge fixture suite and docker compose config.
2. Start the bridge and verify /v1/health over its public HTTPS origin.
3. Verify one stored-PDF conversion, status poll, document fetch, and figure
   fetch with a staging item.
4. Build the app with that exact origin and install the two named credentials.
5. Test the simulator, then an owner-attended Kobo device.
6. Revoke staging credentials and stop the bridge before moving to personal
   data.

The app can still show metadata and Zotero indexed text when the bridge is
absent. Figures remain online-only in the current implementation.
