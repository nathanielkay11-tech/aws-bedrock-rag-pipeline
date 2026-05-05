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

## Phase 2B: Role-Based Access Control

**What it is:**
Cognito-backed authentication ensuring lawyers only query 
documents from matters they are assigned to.

**Why it's deferred:**
Phase 1 assumes a trusted internal user base within a single 
firm. Access control adds significant complexity — Cognito 
user pools, JWT validation in Lambda, matter-level permission 
tables in DynamoDB — without changing the core RAG capability.

**What Phase 2B involves:**
- AWS Cognito user pool for lawyer authentication
- Matter-level permission table in DynamoDB — maps user to 
  permitted matter IDs
- Query Lambda validates JWT token and filters knowledge base 
  query to permitted matters only
- Admin interface for matter assignment management

**Target market:** Any firm handling sensitive multi-client 
matters where information barrier requirements apply.

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