# Testing Log

## Test Environment
- **AWS Region:** eu-west-1
- **Knowledge Base:** vandermeer-legal-kb
- **Frontend:** Local — src/frontend/index.html served via python3 -m http.server 8080
- **Deployment:** Terraform — terraform/

---

## Upload Flow Tests

### TEST-U-001: Single PDF Upload
**Action:** Upload `accenture-supply-agreement.pdf` with matter ID
`accenture-supply-2023`, document type `contracts`, uploader name `Sophie van der Berg`
**Expected:** File appears in S3 at
`matters/accenture-supply-2023/contracts/Sophie van der Berg/accenture-supply-agreement.pdf`.
Ingestion Lambda triggered. Bedrock ingestion job started.
**Result:** ✅ Complete
**Notes:** Ingestion job confirmed COMPLETE via AWS CLI.

---

### TEST-U-002: Unsupported File Type Rejection
**Action:** Attempt to upload a `.xlsx` file via the upload form
**Expected:** Frontend rejects file before upload. Error message
displayed. No S3 upload attempted.
**Result:** ✅ Complete
**Notes:** Frontend validation correctly rejects unsupported file types.

---

### TEST-U-003: Missing Matter ID Validation
**Action:** Attempt to upload a PDF without entering a matter ID
**Expected:** Frontend validation prevents submission.
Error message displayed.
**Result:** ✅ Complete
**Notes:** Frontend validation correctly prevents submission without matter ID.

---

### TEST-U-004: Missing Uploader Name Validation
**Action:** Attempt to upload a PDF without entering uploader name
**Expected:** Frontend validation prevents submission.
Error message displayed.
**Result:** ✅ Complete
**Notes:** Frontend validation correctly prevents submission without uploader name.

---

### TEST-U-005: Full Document Library Upload
**Action:** Upload all seven documents with correct
matter IDs, document types, and uploader names per test-data-manifest.md
**Expected:** All seven documents ingested into knowledge base.
All matters correctly filed.
**Result:** ✅ Complete
**Notes:** 7/7 ingestion jobs confirmed COMPLETE. One document was
re-uploaded after incorrect document type was selected on first attempt.

---

## Query Flow Tests

### TEST-Q-001: Precision Query
**Query:** "What are the termination clauses across all contracts?"
**Matter Filter:** None
**Expected:** Answer references termination clauses from multiple
contracts. Citations show document name, matter ID, page reference,
text excerpt, and uploader name. NDA uploaded live appears in results.
**Result:** ✅ Complete
**Notes:** System returned termination clauses from multiple contracts
including the live-uploaded NDA. Real-time ingestion confirmed.

---

### TEST-Q-002: Cross-Document Query
**Query:** "Which contracts contain automatic renewal provisions
and what are the notice periods?"
**Matter Filter:** None
**Expected:** Answer identifies which contracts contain automatic
renewal provisions and which do not. Notice periods specified.
**Result:** ✅ Complete
**Notes:** System correctly identified automatic renewal provisions
and distinguished contracts with and without them.

---

### TEST-Q-003: Synthesis Query
**Query:** "Summarise the key liability limitations across all contracts"
**Matter Filter:** None
**Expected:** Answer synthesises liability terms across multiple
contract documents. Multiple citations referencing different matters.
**Result:** ✅ Complete
**Notes:** System synthesised liability limitations from 4 documents
simultaneously including Dutch language contract.

---

### TEST-Q-004: Bilingual Query
**Query:** "What are the payment terms and invoicing requirements
in the Dutch supply agreement?"
**Matter Filter:** None
**Expected:** Answer returned in English despite source document
being in Dutch. Citation references Dutch Supply Agreement
uploaded by Lena Kaufmann.
**Result:** ✅ Complete
**Notes:** Answer returned correctly in English. Source citation
excerpt shown in Dutch confirming correct source document retrieved.

---

### TEST-Q-005: Error Query
**Query:** "Are there any criminal liability or fraud-related
penalty clauses across all contracts?"
**Matter Filter:** None
**Expected:** System returns a graceful no results response.
No hallucinated answer. Citations show documents searched.
**Result:** ✅ Complete
**Notes:** System correctly returned no criminal liability clauses
found. Citations showed documents searched, demonstrating
transparent reasoning rather than hallucination.

---

## Deployment Notes

- **Deployment date:** 13 May 2026
- **OpenSearch initialisation time:** ~10-15 minutes per session
- **First successful query:** 13 May 2026
- **Terraform destroy date:** 13 May 2026

**Issues encountered and resolved:**

1. IAM permissions required iterative refinement across two deployment
   sessions. Two custom policies added — TerraformRAGDeployPolicy and
   AOSSServiceLinkedRole inline policy. See ADR-015.

2. OpenSearch vector index must be created manually before first
   terraform apply each session. Run
   `COLLECTION_ENDPOINT=<endpoint> AWS_REGION=eu-west-1 python3 scripts/create_opensearch_index.py`
   See ADR-015 learning note.

3. API Gateway CORS configuration required explicit update via AWS CLI
   to allow browser requests from localhost origin.

4. Bedrock model ID required EU inference profile format
   `eu.anthropic.claude-sonnet-4-5-20250929-v1:0` — standard model IDs
   are not valid for eu-west-1 Knowledge Base queries.

5. API Gateway URL changes on every terraform apply — frontend
   CONFIG.API_BASE_URL must be updated after each deployment.