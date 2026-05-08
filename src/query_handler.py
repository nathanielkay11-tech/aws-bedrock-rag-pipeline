import json
import logging
import os
import re

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Environment — fail fast at cold start if required vars are absent.
# S3_BUCKET_NAME is optional but required for matter_id filtering to work.
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_ID"]
BEDROCK_MODEL_ID = os.environ["BEDROCK_MODEL_ID"]
BEDROCK_REGION = os.environ.get("BEDROCK_REGION", os.environ.get("AWS_REGION", "eu-west-1"))
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

# RetrieveAndGenerate requires a full model ARN. If BEDROCK_MODEL_ID is already
# an ARN (e.g. a cross-region inference profile) use it as-is; otherwise build one.
MODEL_ARN = (
    BEDROCK_MODEL_ID
    if BEDROCK_MODEL_ID.startswith("arn:")
    else f"arn:aws:bedrock:{BEDROCK_REGION}::foundation-model/{BEDROCK_MODEL_ID}"
)

bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=BEDROCK_REGION)

MAX_QUESTION_LEN = 1000
_MATTER_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


# ---------------------------------------------------------------------------
# Request parsing — API Gateway REST (body is a JSON string) and HTTP API
# (body may already be a dict in some proxy configurations) are both handled.
# ---------------------------------------------------------------------------
def _parse_request(event: dict) -> tuple[str, str | None]:
    raw_body = event.get("body") or "{}"
    body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

    question = body.get("question", "").strip()
    matter_id = body.get("matter_id", "").strip() or None
    return question, matter_id


# ---------------------------------------------------------------------------
# Input validation — returns an error string on failure, None on success.
# ---------------------------------------------------------------------------
def _validate(question: str, matter_id: str | None) -> str | None:
    if not question:
        return "'question' is required and must not be empty."
    if len(question) > MAX_QUESTION_LEN:
        return f"'question' must be {MAX_QUESTION_LEN} characters or fewer."
    if matter_id and len(matter_id) > 64:
        return "'matter_id' must be 64 characters or fewer."
    if matter_id and not _MATTER_ID_RE.match(matter_id):
        return "'matter_id' may only contain letters, digits, hyphens, and underscores."
    return None


# ---------------------------------------------------------------------------
# Retrieval filter — narrows the KB vector search to a specific matter's
# documents using a prefix match on the S3 source URI.
# Requires S3_BUCKET_NAME; if it is absent a warning is logged and the query
# runs unfiltered rather than failing the request.
# ---------------------------------------------------------------------------
def _build_retrieval_config(matter_id: str | None) -> dict:
    if not matter_id:
        return {}

    if not S3_BUCKET_NAME:
        logger.warning(
            "matter_id '%s' provided but S3_BUCKET_NAME is not set — "
            "querying across all matters.",
            matter_id,
        )
        return {}

    return {
        "vectorSearchConfiguration": {
            "filter": {
                "startsWith": {
                    "key": "x-amz-bedrock-kb-source-uri",
                    "value": f"s3://{S3_BUCKET_NAME}/matters/{matter_id}/",
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# Citation extraction — flattens Bedrock's nested citation list into a
# deduplicated array ordered by first appearance in the generated answer.
# Each entry includes excerpt, parsed S3 path metadata, and page reference.
# ---------------------------------------------------------------------------
def _extract_citations(raw_citations: list) -> list[dict]:
    seen_uris: set[str] = set()
    results = []

    for citation in raw_citations:
        for ref in citation.get("retrievedReferences", []):
            uri = ref.get("location", {}).get("s3Location", {}).get("uri", "")
            if uri in seen_uris:
                continue
            seen_uris.add(uri)

            # Parse metadata from the S3 URI.
            # Expected: s3://<bucket>/matters/<matter_id>/<document_type>/<uploader_name>/<filename>
            matter_id_parsed = document_type_parsed = uploader_name_parsed = filename_parsed = None
            try:
                # Split off "s3://bucket" prefix, then examine the key segments
                key_parts = uri.split("/", 3)[-1].split("/")
                if len(key_parts) >= 4 and key_parts[0] == "matters":
                    matter_id_parsed     = key_parts[1]
                    document_type_parsed = key_parts[2]
                    uploader_name_parsed = key_parts[3]
                    if len(key_parts) >= 5:
                        filename_parsed = key_parts[4]
            except Exception:
                pass

            # Extract page reference from Bedrock chunk metadata if present.
            # Bedrock KB surfaces page numbers under different keys depending on chunking strategy.
            metadata = ref.get("metadata", {})
            page_reference = (
                metadata.get("x-amz-bedrock-kb-document-page-number")
                or metadata.get("pageNumber")
                or metadata.get("page_number")
            )

            results.append(
                {
                    "excerpt":        ref.get("content", {}).get("text", ""),
                    "source_uri":     uri,
                    "filename":       filename_parsed,
                    "matter_id":      matter_id_parsed,
                    "document_type":  document_type_parsed,
                    "uploader_name":  uploader_name_parsed,
                    "page_reference": page_reference,
                }
            )

    return results


# ---------------------------------------------------------------------------
# Response helpers — enforce a consistent API Gateway envelope shape.
# ---------------------------------------------------------------------------
def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _error(status_code: int, message: str) -> dict:
    return _response(status_code, {"error": message})


# ---------------------------------------------------------------------------
# Handler entry point
# ---------------------------------------------------------------------------
def lambda_handler(event: dict, context) -> dict:
    # ------------------------------------------------------------------
    # Parse and validate the incoming request body
    # ------------------------------------------------------------------
    try:
        question, matter_id = _parse_request(event)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("Failed to parse request body: %s", exc)
        return _error(400, "Request body must be valid JSON.")

    validation_error = _validate(question, matter_id)
    if validation_error:
        return _error(400, validation_error)

    logger.info("Query — matter_id=%s question=%r", matter_id, question[:120])

    # ------------------------------------------------------------------
    # Build the Bedrock RetrieveAndGenerate request.
    # The retrieval config is omitted entirely when no filter applies so
    # Bedrock uses its default number-of-results setting.
    # ------------------------------------------------------------------
    retrieval_config = _build_retrieval_config(matter_id)
    kb_config: dict = {"knowledgeBaseId": KNOWLEDGE_BASE_ID, "modelArn": MODEL_ARN}
    if retrieval_config:
        kb_config["retrievalConfiguration"] = retrieval_config

    # ------------------------------------------------------------------
    # Call Bedrock RetrieveAndGenerate
    # ------------------------------------------------------------------
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": kb_config,
            },
        )
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        logger.error("Bedrock RetrieveAndGenerate failed (%s): %s", code, exc)
        if code in {"ValidationException", "ResourceNotFoundException"}:
            return _error(400, exc.response["Error"]["Message"])
        if code == "ThrottlingException":
            return _error(429, "Bedrock rate limit reached — please retry after a short delay.")
        return _error(502, "Upstream Bedrock service error.")

    # ------------------------------------------------------------------
    # Extract and return the answer with deduplicated source citations
    # ------------------------------------------------------------------
    answer = response.get("output", {}).get("text", "")
    if not answer:
        logger.error("Bedrock returned an empty answer — KB may have no indexed documents.")
        return _error(502, "No answer generated. Ensure the knowledge base has indexed documents.")

    citations = _extract_citations(response.get("citations", []))

    logger.info(
        "Response — answer_length=%d citations=%d", len(answer), len(citations)
    )

    return _response(
        200,
        {
            "answer": answer,
            "citations": citations,
            "matter_id": matter_id,
        },
    )
