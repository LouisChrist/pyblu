# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Keep this file up to date as the codebase evolves — update it when commands, architecture, or conventions change.

## Project Overview

`pyblu` is an async Python library for controlling BluOS players via their HTTP API (port 11000). No authentication is required. The library is published to PyPI and uses `uv` for dependency management.

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

- **`parse.py`** — Stateless XML parsing functions. Each takes `bytes` from the HTTP response and returns a typed entity. Uses `lxml.etree` for parsing. All functions are decorated with `@_wrap_in_unxpected_response_error`.

- **`entities.py`** — Pure `@dataclass` types (`Status`, `Volume`, `SyncStatus`, `PairedPlayer`, `PlayQueue`, `Preset`, `Input`). No logic.

- **`errors.py`** — Exception hierarchy (`PlayerError` → `PlayerUnreachableError` / `PlayerUnexpectedResponseError`) and two decorator factories that wrap exceptions at the Player and parse layers respectively.

### Key Conventions

**Error handling via decorators**: `_wrap_in_unreachable_error` (on Player methods) catches `TimeoutError` and `aiohttp.ClientConnectionError`. `_wrap_in_unxpected_response_error` (on parse functions) catches everything else. Never add try/except inside Player methods or parse functions — let the decorators handle it.

**BluOS API quirks**:
- All operations use HTTP GET, including mutations (play, pause, volume set).
- `inputs()` calls `/RadioBrowse?service=Capture`, not a dedicated inputs endpoint.
- `play_url()` and `play()` both map to the `/Play` endpoint.
- The API uses "master/slave" terminology; the library exposes this as "leader/follower".

**Long polling**: `status()` and `sync_status()` accept an `etag` parameter. When provided, `poll_timeout` must be strictly less than `timeout` — the Player method validates this and raises `ValueError` if violated.

**Session ownership**: `Player` creates and owns its `aiohttp.ClientSession` unless one is passed in. If an external session is passed, the caller is responsible for closing it. Use `async with Player(...) as player:` in normal usage.

### Testing Pattern

Tests use `aioresponses` to mock HTTP calls and `pytest-asyncio` with `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` decorator needed). `pythonpath = "src"` is set in `pyproject.toml` so imports work without installation.

```python
async def test_example():
    with aioresponses() as mocked:
        mocked.get("http://node:11000/SomeEndpoint", status=200, body="<xml/>")
        async with Player("node") as client:
            result = await client.some_method()
        mocked.assert_called_once()
        assert result.field == expected
```

### Adding a New Player Method

1. Add the entity dataclass to `entities.py` if needed, and export it from `__init__.py`.
2. Add a `parse_*` function in `parse.py` decorated with `@_wrap_in_unxpected_response_error`.
3. Add the async method to `Player` in `player.py` decorated with `@_wrap_in_unreachable_error`.
4. Add tests in `tests/test_player.py` (HTTP mock) and `tests/test_parse.py` (parse logic) as appropriate.
