import re

from invoke import task, Context

def _commits_with_version_change(ctx: Context):
    commits = ctx.run("git log --pretty=format:'%h'", hide=True).stdout.split("\n")
    for commit in commits[:-1]:
        diff = ctx.run(f"git diff {commit}~ {commit} pyproject.toml", hide=True).stdout.split("\n")
        version_lines = [line for line in diff if line.startswith("+version = ")]
        if not version_lines:
            continue

        yield commit, version_lines[0].split(" = ")[1].strip("\"")

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

