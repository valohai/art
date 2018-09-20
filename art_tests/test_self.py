import os
from art.command import run_command


def test_selftest(tmpdir):
    tmpdir = str(tmpdir)
    art_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
    suffix = 'latest'
    run_command([
        '--local-source', art_dir,
        '--dest', tmpdir,
        '--suffix', suffix,
    ])
    assert os.path.isfile(os.path.join(tmpdir, suffix, 'art.whl'))
