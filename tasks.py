import os
import shutil
import sys

from invoke import task, Context, Collection
from packaging.version import InvalidVersion, Version
import github
import questionary


def _commits_with_version_change(ctx: Context):
    commits = ctx.run("git log --pretty=format:'%h'", hide=True).stdout.split("\n")
    for commit in commits[:-1]:
        diff = ctx.run(f"git diff {commit}~ {commit} pyproject.toml", hide=True).stdout.split("\n")
        version_lines = [line for line in diff if line.startswith("+version = ")]
        if not version_lines:
            continue

        yield commit, version_lines[0].split(" = ")[1].strip('"')


def _get_tagged_versions(ctx: Context):
    tags = ctx.run("git tag", hide=True).stdout.split("\n")
    versions = []
    for tag in tags:
        if not tag.startswith("v"):
            continue
        try:
            versions.append(str(Version(tag[1:])))
        except InvalidVersion:
            continue
    return versions


def _preview_bump(ctx: Context, *bumps: str) -> Version:
    bump_args = " ".join(f"--bump {bump}" for bump in bumps)
    version = ctx.run(f"uv version --dry-run --short {bump_args}", hide=True).stdout.strip()
    return Version(version)


def _release_choices(ctx: Context, version: Version) -> list[tuple[str, list[str], Version]]:
    if version.is_devrelease:
        return [
            ("Next development release", ["dev"], _preview_bump(ctx, "dev")),
            ("Promote to stable", ["stable"], _preview_bump(ctx, "stable")),
        ]

    choices = []
    for component in ("patch", "minor", "major"):
        title = component.capitalize()
        choices.append((f"{title} release", [component], _preview_bump(ctx, component)))
    for component in ("patch", "minor", "major"):
        title = component.capitalize()
        choices.append((f"{title} development release", [component, "dev"], _preview_bump(ctx, component, "dev")))
    return choices


def _select_release(ctx: Context, version: Version) -> tuple[list[str], Version]:
    releases = _release_choices(ctx, version)
    label_width = max(len(label) for label, _, _ in releases)
    choices = [questionary.Choice(f"{label:<{label_width}}  {release_version}", value=(bumps, release_version)) for label, bumps, release_version in releases]
    return questionary.select(
        f"Select release (current: {version})",
        choices=choices,
        instruction="(Ctrl+C to abort)",
    ).unsafe_ask()


@task
def add_missing_tags(ctx: Context):
    tagged_versions = _get_tagged_versions(ctx)
    missing_commits_with_versions = [x for x in _commits_with_version_change(ctx) if x[1] not in tagged_versions]

    if not missing_commits_with_versions:
        print("No new versions to tag")
        return

    for commit, version in missing_commits_with_versions:
        print(f"Tagging {commit} as {version}")
        ctx.run(f"git tag -m v{version} v{version} {commit}", hide=True)


@task
def release(ctx: Context):
    github_token = os.getenv("GITHUB_TOKEN_PYBLU")
    if github_token is None:
        print("GITHUB_TOKEN_PYBLU environment variable is required")
        sys.exit(1)
    github_auth = github.Auth.Token(github_token)
    gh = github.Github(auth=github_auth)
    try:
        github_repo = gh.get_repo("LouisChrist/pyblu")
    except github.GithubException:
        print("No access to LouisChrist/pyblu")
        sys.exit(1)

    current_branch = ctx.run("git branch --show-current", hide=True).stdout.strip()
    if current_branch != "main":
        print("You must be on the main branch to release")
        sys.exit(1)

    any_changes = ctx.run("git status --porcelain", hide=True).stdout.strip()
    if any_changes:
        print("There are uncommited changes")
        sys.exit(1)

    version = Version(ctx.run("uv version --short", hide=True).stdout.strip())
    bumps, bumped_version = _select_release(ctx, version)

    bump_args = " ".join(f"--bump {bump}" for bump in bumps)
    ctx.run(f"uv version {bump_args}")

    print(f"Creating commit with tag v{bumped_version}")
    ctx.run("git add pyproject.toml", hide=True)
    ctx.run(f"git commit -m 'Release v{bumped_version}'", hide=True)
    ctx.run(f"git tag -m v{bumped_version} v{bumped_version}", hide=True)

    print("Pushing changes")
    ctx.run("git push --follow-tags", hide=True)

    print("Creating release")
    github_repo.create_git_release(
        f"v{bumped_version}",
        f"v{bumped_version}",
        generate_release_notes=True,
        prerelease=bumped_version.is_prerelease,
        make_latest="false" if bumped_version.is_prerelease else "true",
    )

    print(f"Release v{bumped_version} created. CI/CD will build and publish to PyPI.")


@task
def format_and_lint(ctx: Context):
    ctx.run("black src tests")
    ctx.run("pylint -f colorized src tests")


@task
def test(ctx: Context):
    ctx.run("pytest tests --color=yes")


@task
def mypy(ctx: Context):
    ctx.run("mypy src")


@task
def build_docs(ctx: Context):
    print("Building docs")
    ctx.run("sphinx-build -b html docs _site", hide=True)


SHELL = shutil.which("bash") or shutil.which("sh")
ns = Collection.from_module(sys.modules[__name__])
ns.configure({"run": {"shell": SHELL}})
