import os

import pytest

from art.command import run_command


@pytest.mark.parametrize("source", ["local", "git"])
def test_selftest(tmpdir, source, monkeypatch):
    # Hack: Disable pytest-cov subprocess coverage...
    monkeypatch.delitem(os.environ, "COV_CORE_SOURCE", raising=False)

    dest1 = str(tmpdir.join("aaa"))
    dest2 = str(tmpdir.join("bbb"))
    suffix = "latest"
    args = ["--dest", dest1, "--dest", dest2, "--suffix", suffix]
    if source == "local":
        art_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
        args.extend(["--local-source", art_dir])
    elif source == "git":
        args.extend(["--suffix-description"])
        args.extend(["--git-source", "https://github.com/valohai/art.git"])
    run_command(args)
    for dest in (dest1, dest2):
        assert os.path.isfile(os.path.join(dest, suffix, "art.whl"))
