import art.write
from art.config import ArtConfig
from art.manifest import Manifest


def test_dest_options(mocker, tmpdir):
    cfg = ArtConfig(
        work_dir=str(tmpdir), dests=[str(tmpdir)], name="", repo_url=str(tmpdir)
    )
    mf = Manifest(files={})
    wf = mocker.patch("art.write._write_file")
    art.write.write(
        cfg,
        dest="derp://foo/bar/?acl=quux",
        path_suffix="blag",
        manifest=mf,
        dry_run=False,
    )
    call_kwargs = wf.call_args[1]
    assert call_kwargs["options"] == {"acl": "quux"}
    assert call_kwargs["dest"] == "derp://foo/bar/blag/.manifest.json"
