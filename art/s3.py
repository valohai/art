import logging
from urllib.parse import urlparse

s3_client = None
log = logging.getLogger(__name__)


def s3_write(url, source_fp):
    global s3_client
    purl = urlparse(url)
    if not s3_client:
        import boto3

        s3_client = boto3.client("s3")
    assert purl.scheme == "s3"
    s3_client.put_object(Bucket=purl.netloc, Key=purl.path.lstrip("/"), Body=source_fp)
    log.info("Wrote to S3: %s", url)
