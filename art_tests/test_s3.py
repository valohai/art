import io

from art.s3 import get_s3_client
from art.write import _write_file


def test_s3_acl(mocker):
    cli = get_s3_client()
    x = cli.put_object  # avoid magic
    with mocker.patch.object(cli, "put_object"):
        body = io.BytesIO(b"test")
        _write_file("s3://bukkit/key", body, options={"acl": "public-read"})
        cli.put_object.assert_called_with(
            Bucket="bukkit", Key="key", ACL="public-read", Body=body
        )
