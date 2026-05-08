# Phase Two Additions

This document outlines the features and integrations that are 
out of scope for Phase 1 but represent the natural evolution 
of this system toward enterprise readiness.

---

## Phase 2A: Enterprise DMS Integration

**What it is:**
An integration layer connecting the RAG pipeline to existing 
Document Management Systems used by enterprise law firms — 
primarily iManage and NetDocuments.

**Why it's deferred:**
Phase 1 targets small to mid-size firms without existing DMS 
infrastructure. Enterprise firms already have iManage or 
NetDocuments as their source of truth for documents. Building 
this integration in Phase 1 would significantly expand scope 
without changing the core RAG architecture.

**What Phase 2A involves:**
- iManage and NetDocuments API connectors
- Automated document sync from DMS into S3 on document creation or update
- Metadata preserved from source system — matter ID, client, 
  document type, author, date — no re-tagging required
- Bi-directional sync to handle document updates and deletions
- Webhook or polling pattern depending on DMS API capability

**Target market:** Magic Circle firms and large enterprise 
legal departments running iManage or NetDocuments at scale.

---

## Phase 2B: Ethical Walls and Matter-Level Access Control

**What it is:**
Cognito-backed authentication enforcing ethical wall compliance 
at the account level. Each lawyer has an account with 
matter-level permissions assigned by a firm administrator. 
When documents are uploaded they are tagged to specific matters 
and assigned to permitted users. Queries automatically filter 
to the lawyer's permitted matters — no manual filter required.

**Why it's deferred:**
Phase 1 assumes a trusted internal user base where all staff 
are permitted to access all matters. Ethical wall enforcement 
requires authentication infrastructure — Cognito user pools, 
JWT validation, matter permission tables — that significantly 
expands scope beyond the core RAG capability.

**Legal context:**
Ethical walls are a professional and ethical requirement under 
bar association rules in most jurisdictions. Breaching an 
ethical wall can result in attorney discipline, fee forfeiture, 
and firm disqualification from representing clients. Phase 1 
is only suitable for firms where no ethical wall requirements 
exist.

**What Phase 2B involves:**
- AWS Cognito user pool for lawyer authentication
- Matter permission table in DynamoDB — maps lawyer account 
  to permitted matter IDs
- Document upload tags matter ID to permitted users at 
  ingestion time
- Query Lambda validates JWT token and automatically applies 
  matter-level filter — lawyer never needs to type a matter ID
- Admin interface for matter assignment and ethical wall management

**Target market:** Any firm handling matters where conflicts 
of interest exist or where regulatory ethical wall requirements apply.

---

## Phase 2C: Query Audit Trail

**What it is:**
A complete log of every query made — who asked what, when, 
what answer was returned, and which documents were cited.

**Why it's deferred:**
Audit trail adds DynamoDB writes on every query and requires 
a reporting interface to be useful. The core RAG capability 
is valuable without it. Audit trail becomes critical once 
the system handles regulated matters or billable research time.

**What Phase 2C involves:**
- DynamoDB table storing query ID, user, timestamp, question, 
  answer, citations, and matter ID
- CloudWatch dashboard for query volume and latency monitoring
- Optional: daily digest Lambda generating HTML audit report 
  delivered via SNS — same pattern as pipeline project
- Billable time integration — query log exportable for 
  matter billing reconciliation

**Target market:** Firms with compliance requirements or 
those wanting to track associate research time for billing.

---

## Phase 2D: Multi-Language Support

**What it is:**
Support for contracts and queries in languages beyond English — 
relevant for European law firms handling cross-border matters.

**Why it's deferred:**
Phase 1 assumes English-language documents and queries. 
Multilingual support requires embedding model evaluation 
for non-English text and query language detection logic.

**What Phase 2D involves:**
- Evaluate Titan Embed Text v2 performance on Dutch, German, 
  and French legal documents
- Query language detection in Lambda — route to 
  language-appropriate prompt template
- Bedrock prompt templates per supported language
- Test data set covering target European languages

**Target market:** European law firms handling cross-border 
matters — directly relevant to Netherlands market.

---

## Phase 2E: Document Retention Policy

**What it is:**
S3 lifecycle policies enforcing minimum document retention 
periods and preventing accidental deletion of client documents.

**Why it's deferred:**
Phase 1 has no retention enforcement. Acceptable for a demo 
environment but not for production use with real client documents.

**Legal context:**
Law firms in the Netherlands are required to retain client 
documents for a minimum of 7 years under Dutch Bar Association 
rules. Deletion before this period constitutes a professional 
conduct violation.

**What Phase 2E involves:**
- S3 Object Lock preventing deletion within retention period
- S3 lifecycle policy archiving documents to Glacier after 
  active matter closes
- Matter closure workflow triggering retention clock
- Legal hold capability for matters under litigation

**Target market:** Any firm handling real client matters 
in production.

---

## Phase 2F: Batch Upload with Per-Matter Metadata

**What it is:**
Multi-file upload support allowing lawyers to upload multiple 
documents simultaneously when all files belong to the same matter.

**Why it's deferred:**
Phase 1 requires intentional matter ID and uploader name input 
per document. Batch upload is only viable when files share a 
matter — mixing matters in a single batch creates metadata 
errors. Phase 1 single file upload ensures accuracy.

**What Phase 2F involves:**
- Multi-file picker on upload form
- Single matter ID and uploader name applied to entire batch
- Progress indicator showing per-file upload status
- Batch ingestion job triggered once after all files land in S3

**Target market:** Firms onboarding large document libraries 
or uploading multiple documents per matter simultaneously.