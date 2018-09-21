import os

from art.command import run_command

multi_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "multi"))


def test_multi(tmpdir):
    tmpdir = str(tmpdir)
    suffix = "latest"
    args = ["--dest", tmpdir, "--suffix", suffix, "--local-source", multi_dir]
    run_command(args)
    assert os.path.isfile(os.path.join(tmpdir, "a", suffix, "a.txt"))
    assert os.path.isfile(os.path.join(tmpdir, "b", suffix, "b.txt"))
    assert os.path.isfile(os.path.join(tmpdir, "a", suffix, ".manifest.json"))
    assert os.path.isfile(os.path.join(tmpdir, "b", suffix, ".manifest.json"))
