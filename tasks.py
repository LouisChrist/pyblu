import re

from invoke import task, Context
from semver import Version


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
    return [tag[1:] for tag in tags if re.match(r"v\d+\.\d+\.\d+", tag)]


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
    current_branch = ctx.run("git branch --show-current", hide=True).stdout.strip()
    if current_branch != "main":
        print("You must be on the main branch to release")
        exit(1)

    any_changes = ctx.run("git status --porcelain", hide=True).stdout.strip()
    if any_changes:
        print("There are uncommited changes")
        exit(1)

    version = ctx.run("poetry version --short", hide=True).stdout.strip()
    version = Version.parse(version)

    print(f"patch: {version.bump_patch()}")
    print(f"minor: {version.bump_minor()}")
    print(f"major: {version.bump_major()}")
    choice = input("Select version to bump [patch/minor/major]: ")
    match choice:
        case "patch":
            bumped_version = version.bump_patch()
        case "minor":
            bumped_version = version.bump_minor()
        case "major":
            bumped_version = version.bump_major()
        case _:
            print("Invalid choice")
            exit(1)

    ctx.run(f"poetry version {choice}")

    print(f"Creating commit with tag v{bumped_version}")
    ctx.run("git add pyproject.toml", hide=True)
    ctx.run(f"git commit -m 'Release v{bumped_version}'", hide=True)
    ctx.run(f"git tag -m v{bumped_version} v{bumped_version}", hide=True)

    print("Pushing changes")
    ctx.run("git push --follow-tags", hide=True)

    print("Publishing package")
    ctx.run("poetry publish --build")

    print(f"Release v{bumped_version} created and published")


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
