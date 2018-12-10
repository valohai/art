import logging
from urllib.parse import parse_qsl, urlparse

_s3_client = None
log = logging.getLogger(__name__)


def get_s3_client():
    global _s3_client
    if not _s3_client:
        import boto3

        _s3_client = boto3.client("s3")
    return _s3_client


def s3_write(url, source_fp):
    purl = urlparse(url)
    s3_client = get_s3_client()
    assert purl.scheme == "s3"

    query = dict(parse_qsl(purl.query) if purl.query else ())
    acl = query.get("acl")

    kwargs = dict(Bucket=purl.netloc, Key=purl.path.lstrip("/"), Body=source_fp)
    if acl:
        kwargs["ACL"] = acl
    s3_client.put_object(**kwargs)
    log.info("Wrote to S3 (ACL %s): %s", kwargs.get("ACL"), url)
