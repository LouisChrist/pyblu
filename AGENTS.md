# AGENTS.md

Keep this file minimal: record only guidance that cannot be inferred from code,
tests, or existing documentation.

- See `development.md` for setup, checks, and releases; do not duplicate commands here.
- For BluOS endpoint and response specifications, download the official API PDF
  linked in `README.md` directly rather than searching the web. Extract searchable
  text with `pdftotext -layout`; do not commit downloaded reference files.
- Never run setters or other mutating actions against a real player without
  explicit permission. Tests must use mocks or loopback servers, not live hardware.
- Keep audio setting classes independent; do not introduce setting inheritance,
  parser callbacks, or configuration-driven abstractions. Share XML parsing instead.
- For URL-encoding regressions, verify the raw request path with a loopback server:
  query-parsing HTTP mocks can hide canonicalization bugs.
