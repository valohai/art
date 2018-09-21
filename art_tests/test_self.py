import os

import pytest

from art.command import run_command


@pytest.mark.parametrize("source", ["local", "git"])
def test_selftest(tmpdir, source, monkeypatch):
    # Hack: Disable pytest-cov subprocess coverage...
    monkeypatch.delitem(os.environ, "COV_CORE_SOURCE", raising=False)

    tmpdir = str(tmpdir)
    suffix = "latest"
    args = ["--dest", tmpdir, "--suffix", suffix]
    if source == "local":
        art_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
        args.extend(["--local-source", art_dir])
    elif source == "git":
        args.extend(["--suffix-description"])
        args.extend(["--git-source", "https://github.com/valohai/art.git"])
    run_command(args)
    assert os.path.isfile(os.path.join(tmpdir, suffix, "art.whl"))
