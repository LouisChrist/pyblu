# Development guide

## Setup

You'll need Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/LouisChrist/pyblu.git
cd pyblu
uv sync
```

If you use [devenv](https://devenv.sh/), run `devenv shell` before `uv sync`.
The environment provides Python 3.14, uv, and the native XML libraries.

## Tests and checks

Run these before opening a pull request or making a release:

```bash
uv run pytest
uv run pylint src tests
uv run black --check src tests
uv run mypy src
```

To apply formatting, run `uv run black src tests`. You can also use
`uv run invoke format-and-lint` to format the code and then run pylint.

Tests must use mocks or loopback servers, not real players. For URL-encoding
tests, check the raw request path with a loopback server; query-parsing mocks
can hide encoding bugs. Don't change settings or run other mutating commands
on a real player without explicit permission.

For BluOS API details, download the official PDF linked in the
[README](README.md) and extract its text with `pdftotext -layout`. Keep downloaded
reference files out of git.

## Documentation

```bash
uv run invoke build-docs
```

The HTML output is in `_site/`. The docs workflow builds on matching branch
pushes and `v*` tags; only tags deploy to
[GitHub Pages](https://louischrist.github.io/pyblu/).

## Making a release

### Access

Set the `GITHUB_TOKEN_PYBLU` environment variable to a GitHub personal access
token. A fine-grained token needs access to `LouisChrist/pyblu` with read/write
**Contents** permission; a classic token needs the `repo` scope. The release
task uses this token to create the GitHub release. Git pushes use your normal
credentials for `origin`.

PyPI publishing uses Trusted Publisher authentication, not a PyPI API token.
If publishing fails because of authentication, check the project's
[Trusted Publisher settings](https://pypi.org/manage/project/pyblu/settings/publishing/):

| Field | Value |
| --- | --- |
| Owner | `LouisChrist` |
| Repository | `pyblu` |
| Workflow | `release.yml` |
| Environment | `pypi` |

### Release steps

Start from an up-to-date `main` branch with a clean working tree:

```bash
git switch main
git pull --ff-only
git status
```

Run the [tests and checks](#tests-and-checks), then:

```bash
uv run invoke release
```

Choose a version with the arrow keys and press Enter. The menu shows the
resulting version for each choice. Press Ctrl+C at the menu to cancel without
changing anything.

The task updates `pyproject.toml`, creates a `Release v{version}` commit and an
annotated `v{version}` tag, pushes them, and creates a GitHub release with
automatically generated notes. It does not run the local checks for you.

Pushing the tag starts the [release workflow](https://github.com/LouisChrist/pyblu/actions/workflows/release.yml).
It runs lint, formatting, type checks, and tests, then builds the source archive
and wheel and publishes them to PyPI. Check the workflow result before treating
the release as complete.

### Development releases

The same release menu offers patch, minor, and major versions as either stable
or development releases. If the current version is a development release, you
can only increment its development number or promote it to stable.

Development releases use the same publishing workflow and are marked as
pre-releases on GitHub. To install one:

```bash
pip install --pre pyblu
```

### Testing the release build

Open the [release workflow](https://github.com/LouisChrist/pyblu/actions/workflows/release.yml),
choose **Run workflow**, select the branch, and check **Run build without
publishing (dry-run)**.

This runs the checks and builds the packages without publishing to PyPI. The
workflow's `dist` artifact contains the packages for inspection.

## If a release fails

Check the task output and GitHub Actions logs to see which step failed. If no
code change is needed, fix the cause and rerun the failed jobs.

**Check PyPI before rolling anything back.** The tag push starts publishing
before the task creates the GitHub release, so a failure in that last step
doesn't mean the package wasn't published. If only the GitHub release is
missing, create it for the existing tag rather than running the release task
again.

### The version is already on PyPI

Don't delete or reuse the version. If the package needs a fix, commit it, run
the checks, and make a new release. For a development version, choose the next
development number; for a stable version, choose the appropriate version bump.

### The version is not on PyPI

If you need to change the code and retry the same version after pushing the
release commit and tag:

1. Cancel any running release workflow for the tag, then confirm the version
   hasn't appeared on PyPI.
2. Delete the [GitHub release](https://github.com/LouisChrist/pyblu/releases),
   if one exists.
3. Delete the remote and local tags, replacing `{version}` with the version
   you're retrying:

   ```bash
   git push origin :refs/tags/v{version}
   git tag -d v{version}
   ```

4. Find and revert the release commit. Because it was pushed to `main`, use a
   revert rather than rewriting history:

   ```bash
   git log --oneline -n 5
   git revert <release-commit-hash>
   git push origin main
   ```

5. Apply and commit the fix, run the checks, and run `uv run invoke release`
   again. Reverting the version bump lets you select the same target version.

If the task failed before pushing, inspect `git status`, the local commits, and
the tags first. Don't follow the remote rollback steps for changes that only
exist locally.
