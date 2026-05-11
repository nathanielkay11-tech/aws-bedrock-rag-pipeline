import json
import logging
import os
import re

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Environment — fail fast at cold start if required vars are absent
# ---------------------------------------------------------------------------
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

# Pre-signed URL lifetime in seconds — browser must begin the PUT within this window
PRESIGN_EXPIRY = int(os.environ.get("PRESIGN_EXPIRY_SECONDS", "300"))

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc"}
ALLOWED_DOC_TYPES  = {"contracts", "filings", "opinions", "reports"}

# Regex for path segments that must not allow directory traversal or injection
_SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _\-\.]{0,199}$")

# Content-type map used when generating the presigned URL; the browser must
# send the matching Content-Type header in its PUT or S3 will reject the request
_CONTENT_TYPES = {
    ".pdf":  "application/pdf",
    ".txt":  "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc":  "application/msword",
}

# CORS headers included on every response so the browser frontend can call
# this endpoint directly without a same-origin proxy
_CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}

_AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")
# SigV4 + virtual-hosted style produces bucket.s3.region.amazonaws.com URLs.
# Without this, boto3 defaults to SigV2 against the global endpoint, which
# causes a 307 redirect and a 500 on the S3 CORS OPTIONS preflight — both
# of which browsers refuse to follow for cross-origin PUT requests.
s3 = boto3.client(
    "s3",
    region_name=_AWS_REGION,
    config=Config(
        s3={"addressing_style": "virtual"},
        signature_version="s3v4",
    ),
)


# ---------------------------------------------------------------------------
# Input validation — returns an error string on failure, None on success
# ---------------------------------------------------------------------------
def _validate(uploader_name: str, matter_id: str,
              document_type: str, filename: str) -> str | None:
    # Presence checks
    if not uploader_name:
        return "'uploader_name' is required."
    if not matter_id:
        return "'matter_id' is required."
    if not document_type:
        return "'document_type' is required."
    if not filename:
        return "'filename' is required."

    # matter_id: alphanumeric + hyphens + underscores only
    if not re.match(r"^[A-Za-z0-9_\-]{1,64}$", matter_id):
        return "'matter_id' may only contain letters, digits, hyphens, and underscores (max 64 chars)."

    # document_type: must be one of the known categories
    if document_type not in ALLOWED_DOC_TYPES:
        return f"'document_type' must be one of: {', '.join(sorted(ALLOWED_DOC_TYPES))}."

    # filename: safe characters only, no path traversal
    if not _SAFE_SEGMENT_RE.match(filename):
        return "'filename' contains disallowed characters."
    if ".." in filename or "/" in filename:
        return "'filename' must not contain '..' or '/'."

    # uploader_name: safe characters only
    if not _SAFE_SEGMENT_RE.match(uploader_name):
        return "'uploader_name' contains disallowed characters."
    if ".." in uploader_name or "/" in uploader_name:
        return "'uploader_name' must not contain '..' or '/'."

    # File extension must be supported
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return f"'{filename}' has an unsupported extension. Allowed: {sorted(ALLOWED_EXTENSIONS)}."

    return None


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------
def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers":    {"Content-Type": "application/json", **_CORS},
        "body":       json.dumps(body),
    }


def _error(status_code: int, message: str) -> dict:
    return _response(status_code, {"error": message})


# ---------------------------------------------------------------------------
# Handler entry point
# ---------------------------------------------------------------------------
def lambda_handler(event: dict, context) -> dict:
    # ------------------------------------------------------------------
    # Handle CORS preflight — browser sends OPTIONS before the real POST
    # ------------------------------------------------------------------
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    if method == "OPTIONS":
        return _response(200, {})

    # ------------------------------------------------------------------
    # Parse JSON request body
    # ------------------------------------------------------------------
    try:
        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse request body: %s", exc)
        return _error(400, "Request body must be valid JSON.")

    uploader_name = body.get("uploader_name", "").strip()
    matter_id     = body.get("matter_id",     "").strip()
    document_type = body.get("document_type", "").strip()
    filename      = body.get("filename",      "").strip()

    # ------------------------------------------------------------------
    # Validate all fields before touching S3
    # ------------------------------------------------------------------
    validation_error = _validate(uploader_name, matter_id, document_type, filename)
    if validation_error:
        return _error(400, validation_error)

    # ------------------------------------------------------------------
    # Build the S3 key that the ingestion handler expects:
    #   matters/<matter_id>/<document_type>/<uploader_name>/<filename>
    # ------------------------------------------------------------------
    s3_key = f"matters/{matter_id}/{document_type}/{uploader_name}/{filename}"

    ext          = "." + filename.rsplit(".", 1)[-1].lower()
    content_type = _CONTENT_TYPES[ext]

    logger.info(
        "Generating presigned PUT URL — bucket=%s key=%s content_type=%s expires=%ds",
        S3_BUCKET_NAME, s3_key, content_type, PRESIGN_EXPIRY,
    )

    # ------------------------------------------------------------------
    # Generate the pre-signed PUT URL.
    # The ContentType constraint means the browser must send the same
    # Content-Type header in its PUT; S3 rejects mismatches.
    # ------------------------------------------------------------------
    try:
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket":      S3_BUCKET_NAME,
                "Key":         s3_key,
                "ContentType": content_type,
            },
            ExpiresIn=PRESIGN_EXPIRY,
        )
    except ClientError as exc:
        logger.error("Failed to generate presigned URL: %s", exc)
        return _error(502, "Failed to generate upload URL.")

    logger.info("Presigned URL generated for key: %s", s3_key)

    return _response(200, {
        "upload_url":  upload_url,
        "s3_key":      s3_key,
        "s3_uri":      f"s3://{S3_BUCKET_NAME}/{s3_key}",
        "content_type": content_type,
        "expires_in":  PRESIGN_EXPIRY,
    })
