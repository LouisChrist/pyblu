# Development Guide

This guide covers the development workflow for pyblu, including how to release new versions and handle issues that may arise.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/LouisChrist/pyblu.git
cd pyblu
```

2. Install dependencies:
```bash
uv sync
```

3. Run tests and checks:
```bash
uv run pytest              # Run tests
uv run pylint src tests    # Run linting
uv run black src tests     # Format code
uv run mypy src            # Type check
```

## Release Process

The project uses an automated CI/CD pipeline for building and publishing releases to PyPI. The process is triggered when you create and push a version tag.

### Prerequisites

1. **GitHub Token**: Set the `GITHUB_TOKEN_PYBLU` environment variable with a GitHub personal access token that has repository access.

2. **PyPI Trusted Publisher**: The project uses PyPI's Trusted Publisher feature (OIDC authentication) instead of API tokens.

### Creating a Release

1. Ensure you're on the `main` branch with no uncommitted changes:
```bash
git checkout main
git pull
git status  # Should show clean working directory
```

2. Run the release task:
```bash
uv run invoke release
```

3. The script will:
   - Display an interactive list of stable and development version bumps, including their resulting versions
   - Update `pyproject.toml` with the new version
   - Create a git commit with message `Release v{version}`
   - Create a git tag `v{version}`
   - Push the commit and tag to GitHub
   - Create a GitHub release with auto-generated release notes

4. Once the tag is pushed, the CI/CD pipeline automatically:
   - Runs all quality gates (lint, typecheck, test)
   - Builds the package (sdist and wheel)
   - Publishes to PyPI using Trusted Publisher authentication

5. Monitor the release workflow at: https://github.com/LouisChrist/pyblu/actions

### Development Releases

PyPI supports PEP 440 development releases. The normal release command presents stable patch, minor, and major releases alongside their development equivalents, with a preview of every resulting version:

```text
Patch release              2.0.9
Minor release              2.1.0
Major release              3.0.0
Patch development release  2.0.9.dev1
Minor development release  2.1.0.dev1
Major development release  3.0.0.dev1
```

Use the arrow keys to select a release and Enter to confirm it. Press Ctrl+C to abort without changing the version.

When the current version is already a development release, the selector only offers to increment its development number (`2.0.9.dev1` → `2.0.9.dev2`) or promote it to stable (`2.0.9.dev2` → `2.0.9`). Patch, minor, and major bumps are unavailable until the development version has been promoted, preventing the current development target from being skipped. Development versions are published by the normal release workflow and marked as pre-releases on GitHub.

Users can opt into development releases with `pip install --pre pyblu`, or install an exact version with `pip install pyblu==2.0.9.dev2`.

### Dry-Run Testing

To test the build process without actually publishing to PyPI:

1. Go to the GitHub Actions page: https://github.com/LouisChrist/pyblu/actions/workflows/release.yml
2. Click "Run workflow"
3. Check the "Run build without publishing (dry-run)" checkbox
4. Select the branch (usually `main`)
5. Click "Run workflow"

This will run all quality gates and build the package, but skip the PyPI publish step. You can download the built artifacts to inspect them.

## PyPI Trusted Publisher Configuration

Trusted Publisher must be configured once on PyPI. This allows GitHub Actions to publish packages without using API tokens.

### Initial Setup

1. Go to https://pypi.org/manage/account/publishing/
2. If the project already exists on PyPI:
   - Go to https://pypi.org/manage/project/pyblu/settings/publishing/
   - Add a new "Trusted Publisher"
3. If this is the first release:
   - Use "Pending Publisher" at https://pypi.org/manage/account/publishing/

4. Configure with these details:
   - **PyPI Project Name**: `pyblu`
   - **Owner**: `LouisChrist`
   - **Repository name**: `pyblu`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

5. Save the configuration

The GitHub Actions workflow is already configured with the necessary permissions (`id-token: write`) to authenticate using OIDC.

## Release failures

If a release failed some of these steps might be necessary:

### 1. Delete the Git Tag

Delete locally and remotely:
```bash
# Delete local tag
git tag -d v{version}

# Delete remote tag
git push origin :refs/tags/v{version}
```

### 2. Delete the GitHub Release

1. Go to https://github.com/LouisChrist/pyblu/releases
2. Find the release for the version
3. Click "Delete" to remove it

### 3. Revert the Version Commit

```bash
# Find the commit hash of the version bump
git log --oneline -n 5

# Revert the commit
git revert <commit-hash>

# Push the revert
git push origin main
```

### 4. Create a Fixed Release

After rolling back:
1. Fix the issue in the codebase
2. Run the release task again and select the appropriate version to create a new release with the fix

## Troubleshooting

### Release Workflow Fails Quality Gates

If lint, typecheck, or tests fail:
1. The workflow will stop before building/publishing
2. Fix the issues locally
3. The tag already exists, so you need to:
   - Delete the tag (see rollback procedure)
   - Fix the code
   - Run the release task again and select the appropriate version

### Trusted Publisher Authentication Fails

Error: `Authentication failed: OIDC token is invalid or expired`

**Solutions**:
- Verify the Trusted Publisher is configured correctly on PyPI
- Check that the workflow name is exactly `release.yml`
- Ensure the environment name is exactly `pypi`
- Verify the repository owner and name match exactly

### Build Artifacts Are Missing

If the publish step can't find the built packages:
- Check the `build` job completed successfully
- Verify artifacts were uploaded (check the build job logs)
- Ensure artifact name matches in download step (`dist`)

### Version Already Exists on PyPI

If you try to re-release a version:
- PyPI will reject it (versions are immutable)
- You must bump to a new version number
- For a development release, publish the next development number (for example, `1.2.3.dev1` → `1.2.3.dev2`)
- Consider using a post-release version (e.g., `1.2.3.post1`) for stable-release packaging fixes

### GitHub Token Issues

Error: `GITHUB_TOKEN_PYBLU environment variable is required`

**Solutions**:
- Set the environment variable: `export GITHUB_TOKEN_PYBLU=ghp_...`
- Generate a token at: https://github.com/settings/tokens
- Required scopes: `repo` (full repository access)

### Uncommitted Changes

Error: `There are uncommitted changes`

**Solutions**:
- Commit or stash your changes before releasing
- Use `git status` to see what's uncommitted
- The release must be from a clean working directory

## Additional Tasks

### Documentation

Build documentation locally:
```bash
uv run invoke build-docs
```

Documentation is automatically deployed to GitHub Pages when a version tag is pushed.

### Formatting and Linting

Format code and run linters:
```bash
uv run invoke format-and-lint  # Formats with black and runs pylint
```

### Retroactive Tagging

If commits with version changes are missing tags:
```bash
uv run invoke add-missing-tags
```

This will scan git history and create tags for any version bumps that weren't tagged.
