import unittest.mock

import art.write
from art.config import ArtConfig
from art.context import ArtContext
from art.manifest import Manifest


def test_dest_options(monkeypatch, tmpdir):
    cfg = ArtConfig(work_dir=str(tmpdir), dests=[str(tmpdir)], name="", repo_url=str(tmpdir))
    mf = Manifest(files={})
    wf = unittest.mock.MagicMock()
    monkeypatch.setattr(art.write, "_write_file", wf)
    context = ArtContext(dry_run=False)
    art.write.write(
        config=cfg,
        context=context,
        dest="derp://foo/bar/?acl=quux",
        manifest=mf,
        path_suffix="blag",
    )
    call_kwargs = wf.call_args[1]
    assert call_kwargs["options"] == {"acl": "quux"}
    assert call_kwargs["dest"] == "derp://foo/bar/blag/.manifest.json"
