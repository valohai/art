from subprocess import check_call, check_output


def git_clone(config):
    check_call(
        [
            "git",
            "clone",
            "--depth=1",
            "--branch",
            config.ref,
            "--",
            config.repo_url,
            config.work_dir,
        ]
    )


def describe(config):
    description = (
        check_output(["git", "describe", "--always", "--long", "--dirty"], cwd=config.work_dir)
        .decode()
        .strip()
    )
    rev = (
        check_output(["git", "rev-parse", "--", "HEAD"], cwd=config.work_dir)
        .decode()
        .strip()
    )

    return {"id": rev, "description": description}
