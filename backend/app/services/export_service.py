from __future__ import annotations

import csv
import io
import logging
import os
from uuid import UUID

logger = logging.getLogger(__name__)


async def export_to_s3(
    tenant_id: UUID,
    filename: str,
    content: str,
    content_type: str = "text/csv",
) -> str | None:
    """Upload export file to S3 and return the presigned URL.

    Returns None if S3 is not configured (development/testing).
    """
    if os.environ.get("TESTING") == "1":
        return None

    from app.core.config import settings

    if not settings.S3_BUCKET_EXPORTS:
        logger.warning("S3_BUCKET_EXPORTS not configured, skipping upload")
        return None

    try:
        import boto3

        s3 = boto3.client("s3", region_name=settings.AWS_REGION)
        key = f"exports/{tenant_id}/{filename}"

        s3.put_object(
            Bucket=settings.S3_BUCKET_EXPORTS,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType=content_type,
        )

        # Generate presigned URL (valid for 1 hour)
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_EXPORTS, "Key": key},
            ExpiresIn=3600,
        )
        return url
    except Exception:
        logger.exception("Failed to upload to S3")
        return None


def generate_csv(headers: list[str], rows: list[list]) -> str:
    """Generate CSV content from headers and rows."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()
