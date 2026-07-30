# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Keep this file up to date as the codebase evolves — update it when commands, architecture, or conventions change.

## Project Overview

`pyblu` is an async Python library for controlling BluOS players via their HTTP API (port 11000). No authentication is required. The library is published to PyPI and uses `uv` for dependency management.

## BluOS API Documentation

Use the official BluOS Custom Integration API PDF linked near the top of `README.md` as the source of truth for endpoints and response formats. Download that document directly instead of searching the web. To make it searchable locally:

```bash
api_url=$(grep -o 'https://[^)]*\.pdf' README.md | head -1)
curl -fL "$api_url" -o /tmp/bluos-api.pdf
pdftotext -layout /tmp/bluos-api.pdf /tmp/bluos-api.txt
rg -n -C 10 '/Playlist|/Delete|/Move|/Save' /tmp/bluos-api.txt
```

The PDF and extracted text are temporary reference files; do not commit them.

## Commands

```bash
uv sync                          # Install all dependencies (including dev)
uv run pytest                    # Run all tests
uv run pytest tests/test_parse.py::test_parse_status  # Run a single test
uv run pylint src tests          # Lint
uv run black src tests           # Format (line length: 160)
uv run black --check src tests   # Check formatting without modifying
uv run mypy src                  # Type check

# Invoke tasks (wrappers around the above)
uv run invoke format-and-lint    # black + pylint together
uv run invoke test               # pytest
uv run invoke mypy               # mypy
uv run invoke build-docs         # sphinx docs → _site/
uv run invoke release            # interactive release (requires GITHUB_TOKEN_PYBLU env var)
```

## Architecture

The library has four modules with a clear separation of concerns:

- **`player.py`** — `Player` class: the public API. Each method makes one HTTP GET request to the BluOS endpoint, passing arguments as query parameters, then delegates the raw response bytes to a parse function. All methods are async and decorated with `@_wrap_in_unreachable_error`.

- **`parse.py`** — Stateless XML parsing functions. Each takes `bytes` from the HTTP response and returns a typed entity. Uses `lxml.etree` for parsing. All public parse functions are decorated with `@_wrap_in_unxpected_response_error`.

- **`entities.py`** — Pure `@dataclass` types for player state, play queues, and media browsing, including `PlayQueue`, `PlayQueueTrack`, `BrowseResult`, `BrowseItem`, and `ContextMenuAction`. No logic.

- **`errors.py`** — Exception hierarchy (`PlayerError` → `PlayerUnreachableError` / `PlayerUnexpectedResponseError` / `PlayerCommandError` / `PlayerBrowseError`) and decorators/helpers for translating transport, parser, and structured player errors.

### Key Conventions

**Error handling via decorators**: `_wrap_in_unreachable_error` (on Player methods) catches `TimeoutError` and `aiohttp.ClientConnectionError`. `_wrap_in_unxpected_response_error` (on parse functions) catches everything else. Never add try/except inside Player methods or parse functions — let the decorators handle it.

**BluOS API quirks**:
- All operations use HTTP GET, including mutations (play, pause, volume set).
- `inputs()` calls `/RadioBrowse?service=Capture`, not a dedicated inputs endpoint.
- `play_url()` and `play()` both map to the `/Play` endpoint.
- Browse keys, `playURL` / `autoplayURL`, and context-menu action URLs are opaque. They map to `BrowseItem.play_action_url` / `autoplay_action_url`; do not pass them to `Player.play_url()`. Resolve context-menu keys through `context_menu()` and invoke the returned URIs unchanged; actions may mutate playback, the queue, presets, or service favorites.
- `/Playlist` returns queue metadata as child elements for `length=1`, but as attributes for full and paginated listings; `parse_play_queue()` supports both forms.
- The API uses "master/slave" terminology; the library exposes this as "leader/follower".

**Long polling**: `status()` and `sync_status()` accept an `etag` parameter. When provided, `poll_timeout` must be strictly less than `timeout` — the Player method validates this and raises `ValueError` if violated.

**Session ownership**: `Player` creates and owns its `aiohttp.ClientSession` unless one is passed in. If an external session is passed, the caller is responsible for closing it. Use `async with Player(...) as player:` in normal usage.

### Testing Pattern

Tests use `mocket` to mock HTTP calls and `pytest-asyncio` with `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` decorator needed). `pythonpath = "src"` is set in `pyproject.toml` so imports work without installation.

`mocket` patches the OS socket layer, but aiohttp drives I/O through asyncio transports, so the session must be built with `MocketTCPConnector` and passed into `Player(session=...)` (the test's `async with` owns/closes that session — `Player` only closes sessions it created itself). Decorate each test with `@async_mocketize(strict_mode=True)` so any request without a matching registered entry raises `StrictMocketException` instead of falling through to the real network. Registering the full URL **including the query string** preserves query-param verification: `Entry` matches the querystring exactly by default, so a mismatched param means no entry is served and the request errors out in strict mode.

```python
@async_mocketize(strict_mode=True)
async def test_example():
    Entry.single_register(Entry.GET, "http://node:11000/SomeEndpoint?foo=1", status=200, body="<xml/>")
    async with aiohttp.ClientSession(connector=MocketTCPConnector()) as session:
        async with Player("node", session=session) as client:
            result = await client.some_method()

    assert len(Mocket.request_list()) == 1
    assert result.field == expected
```

### Adding a New Player Method

1. Add the entity dataclass to `entities.py` if needed, and export it from `__init__.py`.
2. Add a `parse_*` function in `parse.py` decorated with `@_wrap_in_unxpected_response_error`.
3. Add the async method to `Player` in `player.py` decorated with `@_wrap_in_unreachable_error`.
4. Add tests in `tests/test_player.py` (HTTP mock) and `tests/test_parse.py` (parse logic) as appropriate.
