import io
from unittest.mock import Mock

import pytest
from boto3 import _get_default_session

from art import cloudfront
from art.context import ArtContext
from art.s3 import get_s3_client
from art.write import _write_file


@pytest.fixture(autouse=True)
def aws_fake_credentials(monkeypatch):
    # Makes sure we don't accidentally use real AWS credentials.
    monkeypatch.setattr(_get_default_session()._session, "_credentials", Mock())


def test_s3_acl(monkeypatch):
    cli = get_s3_client()
    cli.put_object = cli.put_object  # avoid magic
    put_object = Mock()
    monkeypatch.setattr(cli, "put_object", put_object)
    body = io.BytesIO(b"test")
    _write_file("s3://bukkit/key", body, options={"acl": "public-read"}, context=ArtContext())
    cli.put_object.assert_called_with(Bucket="bukkit", Key="key", ACL="public-read", Body=body)


def test_s3_invalidate_cloudfront(monkeypatch):
    cli = get_s3_client()
    cli.put_object = cli.put_object  # avoid magic
    put_object = Mock()
    monkeypatch.setattr(cli, "put_object", put_object)
    body = io.BytesIO(b"test")
    options = {"acl": "public-read", "cf-distribution-id": "UWUWU"}
    context = ArtContext()
    _write_file("s3://bukkit/key/foo/bar", body, options=options, context=context)
    _write_file("s3://bukkit/key/baz/quux", body, options=options, context=context)
    _write_file("s3://bukkit/key/baz/barple", body, options=options, context=context)
    cf_client = Mock()
    cf_client.create_invalidation.return_value = {"Invalidation": {"Id": "AAAAA"}}
    monkeypatch.setattr(cloudfront, "get_cloudfront_client", Mock(return_value=cf_client))
    context.execute_post_run_tasks()
    # Assert the 3 files get a single invalidation
    cf_client.create_invalidation.assert_called_once()
    call_kwargs = cf_client.create_invalidation.call_args.kwargs
    assert call_kwargs["DistributionId"] == "UWUWU"
    assert set(call_kwargs["InvalidationBatch"]["Paths"]["Items"]) == {
        "/key/baz/barple",
        "/key/baz/quux",
        "/key/foo/bar",
    }
