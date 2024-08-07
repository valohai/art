from __future__ import annotations

import logging
import time
from typing import Any

log = logging.getLogger(__name__)


# Separated for testing purposes
def get_cloudfront_client() -> Any:
    import boto3

    return boto3.client("cloudfront")


def execute_cloudfront_invalidations(invalidations: dict[str, set[str]]) -> None:
    cf_client = get_cloudfront_client()
    ts = int(time.time())
    for dist_id, paths in invalidations.items():
        log.info("Creating CloudFront invalidation for %s: %d paths", dist_id, len(paths))
        caller_reference = f"art-{dist_id}-{ts}"
        inv = cf_client.create_invalidation(
            DistributionId=dist_id,
            InvalidationBatch={
                "Paths": {
                    "Quantity": len(paths),
                    "Items": sorted(paths),
                },
                "CallerReference": caller_reference,
            },
        )
        log.info(
            "Created CloudFront invalidation with caller reference %s: %s",
            caller_reference,
            inv["Invalidation"]["Id"],
        )
