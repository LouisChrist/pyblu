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
uv run invoke release            # select a stable/dev release (requires GITHUB_TOKEN_PYBLU env var)
```

## Architecture

The library has five main modules with a clear separation of concerns:

- **`player.py`** — `Player` class: the public API. Async endpoint methods use `_get()` to make HTTP GET requests, then delegate the raw response bytes to parse functions. `_get()` centralizes transport error handling.

- **`settings.py`** — Settings API exposed through `Player.settings`. Uses the player's `_get()` callable for requests, sharing its session, timeouts, and transport error handling. Each audio setting has its own independent class (no setting inheritance, parser callbacks, or configuration flags), following the original `ListeningMode`/`SubwooferMode` pattern: store `_get`, query the audio page in `_query_endpoint()`, and use explicit endpoint/query parameters in mutation methods. Share XML parsing in `parse.py`, not setting classes. The original mode methods, value dataclasses (including listening-mode icons), parsers, and availability semantics are retained. `parse_audio_setting()` returns `AudioSetting` metadata, `SettingValue` choices, and `SettingRange` bounds. Tests in `tests/test_settings.py` use the saved N130/N331 XML responses and strict HTTP mocks; never run setters against a real player without explicit permission.

- **`parse.py`** — Stateless XML parsing functions. Each takes `bytes` from the HTTP response and returns a typed entity. Uses `lxml.etree` for parsing. All public parse functions are decorated with `@_wrap_in_unxpected_response_error`.

- **`entities.py`** — Pure `@dataclass` types for player state, play queues, and media browsing, including `PlayQueue`, `PlayQueueTrack`, `BrowseResult`, `BrowseItem`, and `ContextMenuAction`. No logic.

- **`errors.py`** — Exception hierarchy (`PlayerError` → `PlayerUnreachableError` / `PlayerUnexpectedResponseError` / `PlayerCommandError` / `PlayerBrowseError`) and the decorator for translating parser failures.

### Key Conventions

**Centralized error handling**: `Player._get()` catches `TimeoutError` and `aiohttp.ClientConnectionError` and raises `PlayerUnreachableError`. `_wrap_in_unxpected_response_error` on parse functions preserves existing `PlayerError` exceptions and wraps other exceptions in `PlayerUnexpectedResponseError`. Parsers raise `PlayerCommandError` or `PlayerBrowseError` for structured player errors. Do not duplicate try/except handling in endpoint methods or parse functions.

**BluOS API quirks**:
- All operations use HTTP GET, including mutations (play, pause, volume set).
- `inputs()` calls `/RadioBrowse?service=Capture`, not a dedicated inputs endpoint.
- `play_url()` and `play()` both map to the `/Play` endpoint.
- Browse keys, `playURL` / `autoplayURL`, and context-menu action URLs are opaque. They map to `BrowseItem.play_action_url` / `autoplay_action_url` and `ContextMenuAction.action_url`; pass them unchanged to `Player.execute_action()`, never to `Player.play_url()`. Resolve context-menu keys through `context_menu()`; actions may mutate playback, the queue, presets, or service favorites. `execute_action()` passes a relative `yarl.URL(encoded=True)` to `_get()` to preserve its encoding. `_get()` accepts relative strings or `URL` objects, rejects URIs with a scheme or host, and resolves them against the player's base URL; normal endpoint query parameters still use aiohttp's encoding.
- `/Playlist` returns queue metadata as child elements for `length=1`, but as attributes for full and paginated listings; `parse_play_queue()` supports both forms. Optional metadata varies by response and player state: `name`, `modified`, `shuffle`, and `repeat` may be absent and are exposed as `None`.
- The API uses "master/slave" terminology; the library exposes this as "leader/follower".

**Audio settings**: `get()` returns display names for choices, booleans for ON/OFF controls, floats for ranges, and a pair of floats for volume limits. `values()` returns choice entries or range metadata. `is_available()` means advertised, irrespective of `dependsOn` (the original listening/subwoofer modes additionally require at least one choice for backward compatibility); setters never adjust prerequisites or fetch/enforce device-specific bounds. The reset action in saved responses is intentionally not exposed by the library. Parse only `<value>` children when enumerating choices, not `<dependsOn>` nodes. Settings with no explicit URL inherit `/audiomodes` from the menu group.

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

The action-URL encoding regression test uses a loopback aiohttp server to assert the raw request path, since query-parsing mocks can hide URL canonicalization. It never contacts a real player.

### Adding a New Player Method

1. Add the entity dataclass to `entities.py` if needed, and export it from `__init__.py`.
2. Add a `parse_*` function in `parse.py` decorated with `@_wrap_in_unxpected_response_error`.
3. Add the async method to `Player` in `player.py`, using `_get()` for the request and delegating the response to the parser.
4. Add tests in `tests/test_player.py` (HTTP mock) and `tests/test_parse.py` (parse logic) as appropriate.
