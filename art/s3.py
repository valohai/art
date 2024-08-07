import logging
from functools import cache
from typing import IO, Any, Dict
from urllib.parse import urlparse

from art.context import ArtContext

log = logging.getLogger(__name__)


@cache
def get_s3_client() -> Any:
    import boto3

    return boto3.client("s3")


def s3_write(
    url: str,
    source_fp: IO[bytes],
    *,
    options: Dict[str, Any],
    context: ArtContext,
) -> None:
    purl = urlparse(url)
    s3_client = get_s3_client()
    assert purl.scheme == "s3"
    assert not purl.query

    acl = options.get("acl")

    kwargs = dict(Bucket=purl.netloc, Key=purl.path.lstrip("/"), Body=source_fp)
    if acl:
        kwargs["ACL"] = acl

    if context.dry_run:
        log.info("Dry-run: would write to S3 (ACL %s): %s", acl, url)
        return
    s3_client.put_object(**kwargs)
    log.info("Wrote to S3 (ACL %s): %s", acl, url)
