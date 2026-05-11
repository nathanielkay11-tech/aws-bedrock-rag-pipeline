"""
Idempotently create the legal-contracts-index in the AOSS collection.
Called by Terraform null_resource on every apply — safe to run repeatedly.

Required env vars:
  COLLECTION_ENDPOINT  e.g. https://<id>.eu-west-1.aoss.amazonaws.com
  AWS_REGION           e.g. eu-west-1
  INDEX_NAME           e.g. legal-contracts-index
"""
import os
import sys

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy import exceptions as os_exc
from requests_aws4auth import AWS4Auth

ENDPOINT = os.environ["COLLECTION_ENDPOINT"]
REGION   = os.environ["AWS_REGION"]
INDEX    = os.environ.get("INDEX_NAME", "legal-contracts-index")

session = boto3.Session()
creds   = session.get_credentials().get_frozen_credentials()
auth    = AWS4Auth(
    creds.access_key,
    creds.secret_key,
    REGION,
    "aoss",
    session_token=creds.token,
)

client = OpenSearch(
    hosts=[{"host": ENDPOINT.replace("https://", ""), "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

INDEX_BODY = {
    "settings": {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
        }
    },
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "faiss",
                    "parameters": {"ef_construction": 512, "m": 16},
                },
            },
            "text":     {"type": "text"},
            "metadata": {"type": "text"},
        }
    },
}


def main() -> None:
    if client.indices.exists(index=INDEX):
        print(f"[opensearch] Index '{INDEX}' already exists — skipping.")
        return

    try:
        resp = client.indices.create(index=INDEX, body=INDEX_BODY)
        print(f"[opensearch] Created index '{INDEX}': {resp}")
    except os_exc.RequestError as exc:
        # resource_already_exists_exception — concurrent create, treat as success
        if "resource_already_exists_exception" in str(exc).lower():
            print(f"[opensearch] Index '{INDEX}' already exists (race) — skipping.")
        else:
            print(f"[opensearch] RequestError creating index: {exc}", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"[opensearch] Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
