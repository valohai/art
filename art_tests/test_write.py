from art.config import ArtConfig
from art.manifest import Manifest
import art.write


def test_dest_options(mocker):
    cfg = ArtConfig()
    mf = Manifest(files={})
    wf = mocker.patch('art.write._write_file')
    art.write.write(cfg, dest='derp://foo/bar/?acl=quux', path_suffix='blag', manifest=mf)
    call_kwargs = wf.call_args[1]
    assert call_kwargs['options'] == {'acl': 'quux'}
    assert call_kwargs['dest'] == 'derp://foo/bar/blag/.manifest.json'
