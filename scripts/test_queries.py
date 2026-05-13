"""
Run the five standard test queries against the live API Gateway endpoint
and write results to docs/test-results.md.

Usage:
    python3 scripts/test_queries.py
"""

import json
import sys
import textwrap
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ⚠️ Update this URL after every terraform apply — API Gateway ID changes each deployment
API_URL = "https://957ilvvg70.execute-api.eu-west-1.amazonaws.com/query"

API_URL = "https://957ilvvg70.execute-api.eu-west-1.amazonaws.com/query"
RESULTS_PATH = Path(__file__).parent.parent / "docs" / "test-results.md"
TIMEOUT = 60  # seconds per request

QUERIES = [
    {
        "question": "What are the termination clauses across all contracts?",
        "matter_id": None,
    },
    {
        "question": "Which contracts contain automatic renewal provisions and what are the notice periods?",
        "matter_id": None,
    },
    {
        "question": "Summarise the key liability limitations across all contracts",
        "matter_id": None,
    },
    {
        "question": "What are the payment terms and invoicing requirements in the Dutch supply agreement?",
        "matter_id": None,
    },
    {
        "question": "Are there any criminal liability or fraud-related penalty clauses across all contracts?",
        "matter_id": None,
    },
]


def post(url: str, payload: dict, timeout: int) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def format_citations_terminal(citations: list) -> str:
    if not citations:
        return "  (no citations returned)"
    lines = []
    for i, c in enumerate(citations, 1):
        filename = c.get("filename") or c.get("source_uri", "unknown").split("/")[-1]
        matter   = c.get("matter_id", "")
        doc_type = c.get("document_type", "")
        uploader = c.get("uploader_name", "")
        page     = c.get("page_reference")
        excerpt  = c.get("excerpt", "")

        meta_parts = [p for p in [matter, doc_type, uploader, f"p.{int(page)}" if page is not None else ""] if p]
        meta = "  |  ".join(meta_parts)

        lines.append(f"  [{i}] {filename}")
        if meta:
            lines.append(f"      {meta}")
        if excerpt:
            wrapped = textwrap.fill(excerpt[:200], width=76, initial_indent="      ", subsequent_indent="      ")
            lines.append(wrapped)
    return "\n".join(lines)


def format_citations_markdown(citations: list) -> str:
    if not citations:
        return "_No citations returned._"
    rows = ["| File | Matter | Type | Uploader | Page |",
            "|------|--------|------|----------|------|"]
    for c in citations:
        filename = c.get("filename") or c.get("source_uri", "").split("/")[-1]
        matter   = c.get("matter_id", "")
        doc_type = c.get("document_type", "")
        uploader = c.get("uploader_name", "")
        page     = c.get("page_reference")
        page_str = str(int(page)) if page is not None else ""
        rows.append(f"| `{filename}` | {matter} | {doc_type} | {uploader} | {page_str} |")
    lines = "\n".join(rows)

    excerpts = []
    for i, c in enumerate(citations, 1):
        if c.get("excerpt"):
            excerpts.append(f"**[{i}]** {c['excerpt'][:300]}{'…' if len(c['excerpt']) > 300 else ''}")
    if excerpts:
        lines += "\n\n**Excerpts**\n\n" + "\n\n".join(excerpts)
    return lines


def run():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md_sections = [
        f"# Test Query Results\n",
        f"**Run:** {timestamp}  ",
        f"**Endpoint:** `{API_URL}`\n",
    ]

    total = len(QUERIES)
    passed = 0

    for i, q in enumerate(QUERIES, 1):
        question  = q["question"]
        matter_id = q["matter_id"]
        payload   = {"question": question}
        if matter_id:
            payload["matter_id"] = matter_id

        filter_label = f"matter={matter_id}" if matter_id else "all matters"

        print(f"\n{'='*72}")
        print(f"Query {i}/{total}  [{filter_label}]")
        print(f"  {question}")
        print(f"{'='*72}")

        try:
            result = post(API_URL, payload, TIMEOUT)
        except Exception as exc:
            error_msg = f"REQUEST FAILED: {exc}"
            print(f"  ✗ {error_msg}")
            md_sections.append(f"## Query {i}\n\n**Question:** {question}  \n**Filter:** {filter_label}\n\n> ❌ {error_msg}\n")
            continue

        # The endpoint returns the API Gateway envelope directly when called
        # via the CLI test harness; unwrap if the body is a JSON string.
        if "body" in result and isinstance(result["body"], str):
            result = json.loads(result["body"])

        answer    = result.get("answer", "")
        citations = result.get("citations", [])
        error     = result.get("error")

        if error:
            print(f"  ✗ API error: {error}")
            md_sections.append(f"## Query {i}\n\n**Question:** {question}  \n**Filter:** {filter_label}\n\n> ❌ API error: {error}\n")
            continue

        passed += 1
        print(f"\nAnswer:\n")
        for line in textwrap.wrap(answer, width=72):
            print(f"  {line}")
        print(f"\nCitations ({len(citations)}):\n")
        print(format_citations_terminal(citations))

        md_answer = answer.replace("\n", "\n\n")
        md_sections.append(
            f"## Query {i}\n\n"
            f"**Question:** {question}  \n"
            f"**Filter:** {filter_label}\n\n"
            f"### Answer\n\n"
            f"{md_answer}\n\n"
            f"### Citations\n\n"
            f"{format_citations_markdown(citations)}\n"
        )

    print(f"\n{'='*72}")
    print(f"Results: {passed}/{total} queries succeeded")
    print(f"{'='*72}\n")

    md_sections.append(f"---\n_Results: {passed}/{total} queries succeeded._\n")
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text("\n".join(md_sections), encoding="utf-8")
    print(f"Results written to {RESULTS_PATH}")


if __name__ == "__main__":
    run()
