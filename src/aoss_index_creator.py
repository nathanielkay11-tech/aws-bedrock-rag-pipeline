"""
Lambda handler: idempotently creates an OpenSearch Serverless index.
"""
import json
import os

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.httpsession import URLLib3Session

REGION   = os.environ.get("AWS_REGION", "eu-west-1")
_session = boto3.Session()
_http    = URLLib3Session()

INDEX_BODY = json.dumps({
    "settings": {"index": {"knn": True, "knn.algo_param.ef_search": 512}},
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,
                "method": {
                    "name": "hnsw", "space_type": "l2", "engine": "faiss",
                    "parameters": {"ef_construction": 512, "m": 16},
                },
            },
            "text":     {"type": "text"},
            "metadata": {"type": "text"},
        }
    },
}).encode()


def _request(method, url, body=None):
    headers  = {"Content-Type": "application/json"} if body else {}
    aws_req  = AWSRequest(method=method, url=url, data=body, headers=headers)
    SigV4Auth(_session.get_credentials(), "aoss", REGION).add_auth(aws_req)
    prepped  = aws_req.prepare()
    print(f"[aoss-debug] {method} {url}")
    print(f"[aoss-debug] signed headers: {dict(prepped.headers)}")
    resp = _http.send(prepped)
    print(f"[aoss-debug] status: {resp.status_code}")
    print(f"[aoss-debug] resp headers: {dict(resp.headers)}")
    body_text = resp.content.decode(errors="replace") if resp.content else ""
    print(f"[aoss-debug] body: {body_text[:500]!r}")
    return resp, body_text


def handler(event, context):
    endpoint = event["endpoint"]
    index    = event["index"]
    url      = f"{endpoint}/{index}"

    # Log the Lambda's own identity
    try:
        identity = boto3.client("sts", region_name=REGION).get_caller_identity()
        print(f"[aoss-debug] Lambda identity: {identity['Arn']}")
    except Exception as exc:
        print(f"[aoss-debug] Could not get identity: {exc}")

    resp, body = _request("HEAD", url)
    if resp.status_code == 200:
        print(f"[aoss] Index '{index}' already exists — skipping.")
        return {"status": "exists", "index": index}
    if resp.status_code != 404:
        raise RuntimeError(f"Unexpected status checking index: {resp.status_code} {body}")

    resp, body = _request("PUT", url, INDEX_BODY)
    if resp.status_code in (200, 201):
        print(f"[aoss] Created index '{index}': {body}")
        return {"status": "created", "index": index}
    if "resource_already_exists_exception" in body.lower():
        print(f"[aoss] Index '{index}' already exists (race).")
        return {"status": "exists", "index": index}

    raise RuntimeError(f"AOSS index creation failed ({resp.status_code}): {body}")
