import json
import logging
import os
import urllib.parse

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Environment — fail fast at cold start if required vars are absent
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
DATA_SOURCE_ID = os.environ["DATA_SOURCE_ID"]

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc"}

bedrock_agent = boto3.client("bedrock-agent")


# ---------------------------------------------------------------------------
# Metadata extraction
#
# Expected S3 key convention:
#   matters/<matter_id>/<document_type>/<filename>
#   e.g. matters/ABC-2024-001/contracts/service-agreement.pdf
#
# matter_id    — unique matter reference used for filtering and logging
# document_type — broad category (contracts, amendments, exhibits, …)
# filename      — original document name including extension
# ---------------------------------------------------------------------------
def _parse_matter_metadata(key: str) -> dict:
    parts = key.split("/")
    if len(parts) < 4 or parts[0] != "matters":
        raise ValueError(
            f"Unexpected key structure '{key}'. "
            "Expected: matters/<matter_id>/<document_type>/<filename>"
        )
    return {
        "matter_id": parts[1],
        "document_type": parts[2],
        # Preserve any sub-path within the filename segment
        "filename": "/".join(parts[3:]),
    }


# ---------------------------------------------------------------------------
# File-type guard — reject unsupported formats before hitting Bedrock
# ---------------------------------------------------------------------------
def _assert_supported(filename: str) -> None:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"File '{filename}' has unsupported extension '{ext}'. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )


# ---------------------------------------------------------------------------
# Ingestion job — starts a Bedrock KB sync for the full data source.
# A ConflictException means a job is already running; we log and skip rather
# than failing, because the in-flight job will pick up the new document.
# ---------------------------------------------------------------------------
def _start_ingestion_job(matter_id: str, filename: str) -> str | None:
    description = f"Triggered by upload: matter={matter_id} file={filename}"
    try:
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=DATA_SOURCE_ID,
            description=description,
        )
        job_id = response["ingestionJob"]["ingestionJobId"]
        logger.info("Ingestion job started: %s", job_id)
        return job_id
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code == "ConflictException":
            # An active job will already ingest the new document on completion
            logger.warning(
                "Ingestion job already in progress for data source %s — skipping.",
                DATA_SOURCE_ID,
            )
            return None
        raise


# ---------------------------------------------------------------------------
# Handler entry point
# ---------------------------------------------------------------------------
def lambda_handler(event: dict, context) -> dict:
    results = []

    # S3 can batch multiple records into one invocation
    for record in event.get("Records", []):
        # ------------------------------------------------------------------
        # Extract bucket and key from the S3 event record
        # ------------------------------------------------------------------
        bucket = record["s3"]["bucket"]["name"]
        # Keys are URL-encoded by S3; decode before any path manipulation
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        size = record["s3"]["object"].get("size", 0)

        logger.info("Processing s3://%s/%s (%d bytes)", bucket, key, size)

        # ------------------------------------------------------------------
        # Parse matter metadata embedded in the key path
        # ------------------------------------------------------------------
        try:
            metadata = _parse_matter_metadata(key)
        except ValueError as exc:
            logger.error("Skipping record — metadata parse failed: %s", exc)
            results.append({"key": key, "status": "skipped", "reason": str(exc)})
            continue

        logger.info(
            "Matter metadata — matter_id=%s document_type=%s filename=%s",
            metadata["matter_id"],
            metadata["document_type"],
            metadata["filename"],
        )

        # ------------------------------------------------------------------
        # Validate file type before triggering an ingestion job
        # ------------------------------------------------------------------
        try:
            _assert_supported(metadata["filename"])
        except ValueError as exc:
            logger.warning("Skipping record — unsupported file type: %s", exc)
            results.append({"key": key, "status": "skipped", "reason": str(exc)})
            continue

        # ------------------------------------------------------------------
        # Trigger Bedrock Knowledge Base ingestion
        # ------------------------------------------------------------------
        job_id = _start_ingestion_job(metadata["matter_id"], metadata["filename"])

        results.append(
            {
                "key": key,
                "status": "ingestion_started" if job_id else "job_already_running",
                "job_id": job_id,
                "matter_id": metadata["matter_id"],
                "document_type": metadata["document_type"],
            }
        )

    return {"statusCode": 200, "body": json.dumps(results)}
