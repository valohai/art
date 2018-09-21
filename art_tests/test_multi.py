import os
import tarfile

from art.command import run_command

multi_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "multi"))
files_per_name = {
    "a": {".manifest.json", "a.txt", "aa/a2.txt"},
    "b": {".manifest.json", "b.txt"},
}


def test_multi(tmpdir):
    tmpdir = str(tmpdir)
    suffix = "latest"
    args = ["--dest", tmpdir, "--suffix", suffix, "--local-source", multi_dir]
    run_command(args)
    for name, files in files_per_name.items():
        for file in files:
            assert os.path.isfile(os.path.join(tmpdir, name, suffix, file))

    tar_path = os.path.join(tmpdir, "a", suffix, "wrap.tar")
    with tarfile.open(tar_path, "r") as tf:
        assert set(tf.getnames()) == files_per_name["a"]
