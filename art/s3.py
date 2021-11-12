import logging
from typing import IO, Any, Dict
from urllib.parse import urlparse

_s3_client = None
log = logging.getLogger(__name__)


def get_s3_client() -> Any:
    global _s3_client
    if not _s3_client:
        import boto3

        _s3_client = boto3.client("s3")
    return _s3_client


def s3_write(
    url: str, source_fp: IO[bytes], *, options: Dict[str, Any], dry_run: bool
) -> None:
    purl = urlparse(url)
    s3_client = get_s3_client()
    assert purl.scheme == "s3"
    assert not purl.query

    acl = options.get("acl")

    kwargs = dict(Bucket=purl.netloc, Key=purl.path.lstrip("/"), Body=source_fp)
    if acl:
        kwargs["ACL"] = acl

    if dry_run:
        log.info("Dry-run: would write to S3 (ACL %s): %s", acl, url)
        return
    s3_client.put_object(**kwargs)
    log.info("Wrote to S3 (ACL %s): %s", acl, url)
