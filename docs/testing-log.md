# Testing Log

## Test Environment
- **AWS Region:** eu-west-1
- **Knowledge Base:** vandermeer-legal-kb
- **Frontend:** Local — src/frontend/index.html
- **Deployment:** Terraform — terraform/

---

## Upload Flow Tests

### TEST-U-001: Single PDF Upload
**Action:** Upload `accenture-supply-agreement.pdf` with matter ID 
`accenture-supply-2023` and uploader name `Sophie van der Berg`
**Expected:** File appears in S3 at 
`matters/accenture-supply-2023/contracts/accenture-supply-agreement.pdf`. 
Ingestion Lambda triggered. Bedrock ingestion job started.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-U-002: Unsupported File Type Rejection
**Action:** Attempt to upload a `.xlsx` file via the upload form
**Expected:** Frontend rejects file before upload. Error message 
displayed. No S3 upload attempted.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-U-003: Missing Matter ID Validation
**Action:** Attempt to upload a PDF without entering a matter ID
**Expected:** Frontend validation prevents submission. 
Error message displayed.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-U-004: Missing Uploader Name Validation
**Action:** Attempt to upload a PDF without entering uploader name
**Expected:** Frontend validation prevents submission. 
Error message displayed.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-U-005: Full Document Library Upload
**Action:** Upload all seven documents off-camera with correct 
matter IDs and uploader names per test-data-manifest.md
**Expected:** All seven documents ingested into knowledge base. 
All matters correctly filed.
**Result:** 🔄 Pending
**Notes:**

---

## Query Flow Tests

### TEST-Q-001: Precision Query with Matter Filter
**Query:** "What are the termination clauses in this matter?"
**Matter Filter:** `accenture-supply-2023`
**Expected:** Answer references termination clauses from Accenture 
Supply Agreement and NDA. Citations show document name, matter ID, 
page reference, text excerpt, and uploader name.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-Q-002: Cross-Document Query — No Filter
**Query:** "Which contracts contain automatic renewal provisions 
and what are the notice periods?"
**Matter Filter:** None
**Expected:** Answer references automatic renewal clauses across 
Accenture Supply Agreement, Employment Contract, and Dutch Supply 
Agreement. Multiple citations returned.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-Q-003: Synthesis Query — No Filter
**Query:** "Summarise the key liability limitations across all 
contracts in no more than five concise bullet points."
**Matter Filter:** None
**Expected:** Answer returns maximum five bullet points 
synthesising liability terms across all contract documents. 
Multiple citations referencing different matters.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-Q-004: Bilingual Query — Dutch Document
**Query:** "What are the payment terms and invoicing requirements in the Dutch supply agreement?"
**Matter Filter:** None
**Expected:** Answer returned in English despite source document 
being in Dutch. Citation references Dutch Supply Agreement 
uploaded by Lena Kaufmann.
**Result:** 🔄 Pending
**Notes:**

---

### TEST-Q-005: Error Query — No Relevant Results
**Query:** "Are there any criminal liability or fraud-related penalty clauses across all contracts?"
**Matter Filter:** None
**Expected:** System returns a graceful no results response. 
No hallucinated answer. No citations returned.
**Result:** 🔄 Pending
**Notes:**
---

## Deployment Notes

- Deployment date: 06 May 2026
- OpenSearch initialisation time: ~10 minutes
- Issues encountered: Two custom IAM policies required — TerraformRAGDeployPolicy and AOSSServiceLinkedRole inline policy. See ADR-015.
- First successful query: Pending
- Terraform destroy date: TBD