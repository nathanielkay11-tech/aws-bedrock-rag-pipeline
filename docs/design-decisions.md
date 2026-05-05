# Architecture Design Decisions

## ADR-001: Separate Terraform Files Over Single main.tf
**Date:** 05 May 2026
**Decision:** Structure Terraform code across separate files by 
concern rather than consolidating into a single main.tf.
**Reason:** Initial code generation produced a single monolithic 
main.tf. Human-in-the-loop review identified this as inconsistent 
with professional Terraform standards. Separate files by concern — 
S3, Knowledge Base, IAM, Lambda — means each component can be 
updated independently without risk of breaking unrelated 
infrastructure. This is the professional standard for maintainable 
IaC at scale.
**Note:** This decision was caught and overridden during AI-assisted 
code review — human architectural governance identified a structural 
problem in generated output and corrected it before it was committed.
**Outcome:** Terraform code separated into purpose-specific files. 
main.tf retained only for provider configuration and shared locals.

---

## ADR-002: OpenSearch Serverless as Vector Store
**Date:** 05 May 2026
**Decision:** Use Amazon OpenSearch Serverless as the vector store 
for the Bedrock Knowledge Base.
**Reason:** RAG requires semantic search — finding content that is 
conceptually similar to a query even when exact keywords don't match. 
A user asking "what happens if I exit the contract early" must find 
clauses about "early termination penalties." Standard keyword search 
cannot do this. OpenSearch Serverless provides managed vector search 
with no infrastructure to maintain — capacity scales automatically 
and AWS handles all index management.
**Alternatives considered:** Self-managed OpenSearch, Pinecone, 
pgvector on RDS. All require additional infrastructure management 
or introduce external dependencies outside the AWS ecosystem.
**Outcome:** OpenSearch Serverless VECTORSEARCH collection 
provisioned via Terraform with Bedrock-scoped access policies.

---

## ADR-003: Amazon Titan Embed Text v2 as Embedding Model
**Date:** 05 May 2026
**Decision:** Use Amazon Titan Embed Text v2 to generate vector 
embeddings for ingested contract documents.
**Reason:** Embedding converts document text into numerical vectors 
that the vector store can index and compare against query vectors. 
Titan Embed Text v2 is Amazon's native embedding model — natively 
integrated with Bedrock Knowledge Bases with no additional 
configuration required. It is the most cost effective option for 
this use case with no meaningful quality tradeoff versus third 
party alternatives for legal document retrieval.
**Alternatives considered:** Cohere Embed — higher cost, requires 
additional integration configuration, no material quality advantage 
for this use case.
**Outcome:** Titan Embed Text v2 configured as the embedding model 
in the Knowledge Base vector configuration block.

---

## ADR-004: Lambda as Query Handler Over Step Functions
**Date:** 05 May 2026
**Decision:** Use a single Lambda function to handle RAG queries 
rather than an AWS Step Functions state machine.
**Reason:** The query flow is a single operation — receive question, 
call Bedrock RetrieveAndGenerate, return answer with citations. 
Step Functions adds value when there are multiple sequential steps 
with conditional branching, error handling between states, or 
long-running workflows requiring human approval. None of those 
conditions apply here. Lambda is simpler, cheaper, and faster 
for a single retrieve-and-generate operation.
**Alternatives considered:** Step Functions — relevant if the 
pipeline required multi-step document validation, conditional 
routing, or human review workflows. Documented as a Phase 2 
consideration if query complexity increases.
**Outcome:** Single Lambda function with direct Bedrock 
RetrieveAndGenerate API call. Response includes answer text 
and source citations returned to API Gateway.

---

## ADR-005: Automated Ingestion via Dedicated Lambda Over Manual Sync
**Date:** 05 May 2026
**Decision:** Implement a dedicated ingestion Lambda triggered by 
S3 events to automatically sync new documents into the Bedrock 
Knowledge Base.
**Reason:** A business would not manually trigger an ingestion job 
every time a document is added. Users uploading contracts expect 
them to be immediately queryable without any manual intervention. 
Automated ingestion is the production standard — the moment a PDF 
lands in S3, Bedrock starts indexing it without human involvement.
**Alternatives considered:** Manual ingestion via CLI or console — 
acceptable for a demo but not viable in any production environment 
where multiple users are uploading documents.
**Outcome:** Separate ingestion Lambda function triggered by 
S3 ObjectCreated events, distinct from the query handler Lambda. 
Single responsibility — one Lambda ingests, one Lambda queries.

---

## ADR-006: Query Response Includes Answer and Source Citations
**Date:** 05 May 2026
**Decision:** The query Lambda returns both the generated answer 
and the source citations referencing the specific document, clause, 
and page number the answer was drawn from.
**Reason:** Legal professionals cannot act on an unverifiable answer. 
A lawyer needs to know exactly which contract, which clause, and 
which page the answer came from — both to verify accuracy and to 
cite the source in their own work. An answer without citations has 
no professional utility in a legal context.
**Alternatives considered:** Answer only — faster response, simpler 
implementation, but unusable in a legal professional context where 
source verification is a professional requirement.
**Outcome:** Bedrock RetrieveAndGenerate returns citations natively. 
Lambda extracts and formats both the answer text and citation 
metadata — document name, page reference, and relevant chunk — 
before returning to API Gateway.

---

## ADR-007: S3 Folder Structure as Metadata Convention
**Date:** 05 May 2026
**Decision:** Use S3 folder path as the metadata convention for 
document organisation rather than filename conventions or 
companion JSON files.
**Reason:** Lawyers should not be required to follow complex 
naming conventions or upload additional metadata files alongside 
documents. An S3 folder structure — `matters/matter-name/document-type/filename.pdf` 
— is intuitive, requires no technical knowledge, and automatically 
provides matter ID and document type metadata that the ingestion 
Lambda can extract from the path without any additional input 
from the user.
**Alternatives considered:** Filename convention — error-prone 
and requires user training. Companion JSON metadata file — 
adds friction to every upload. Both rejected in favour of 
folder structure which lawyers already understand from 
existing file management habits.
**Outcome:** Ingestion Lambda extracts matter ID and document 
type from S3 object key path. Documents automatically tagged 
with correct metadata on ingestion without user intervention.

---

## ADR-008: Phase 1 Targets Standalone Small to Mid-Size Firms
**Date:** 05 May 2026
**Decision:** Phase 1 targets small to mid-size law firms 
without existing Document Management Systems. Enterprise 
DMS integration deferred to Phase 2.
**Reason:** Small to mid-size firms without iManage or 
NetDocuments infrastructure represent an immediately 
addressable market that can adopt this system without 
integration complexity. Building DMS integration into 
Phase 1 would significantly expand scope without changing 
the core RAG architecture. The standalone upload pattern 
is production grade for this target segment.
**Phase 2:** Enterprise integration layer connecting to 
iManage and NetDocuments — documents flow automatically 
from existing DMS into S3 with metadata already attached 
from the source system. See `docs/phase-two-additions.md`.
**Outcome:** Phase 1 delivers a complete standalone RAG 
system for small to mid-size firms. Phase 2 roadmap 
documented separately.

---

## ADR-009: Knowledge Base ID Passed via Terraform Environment Variable
**Date:** 05 May 2026
**Decision:** Terraform passes the Bedrock Knowledge Base ID to 
the ingestion Lambda as an environment variable at deploy time.
**Reason:** The alternative — Lambda fetching the Knowledge Base 
ID dynamically at runtime via an API call — adds unnecessary 
latency to every invocation and requires additional IAM 
permissions. The Knowledge Base ID is stable after deployment 
and Terraform automatically updates the environment variable 
if the Knowledge Base is ever recreated.
**Alternatives considered:** Dynamic runtime lookup via 
boto3 describe call — rejected due to unnecessary API overhead 
on every invocation with no meaningful benefit.
**Outcome:** Knowledge Base ID injected as Lambda environment 
variable by Terraform at deploy time. No runtime API calls 
required to resolve the ID.

---

## ADR-010: HTML Frontend Covers Both Upload and Query Flows
**Date:** 05 May 2026
**Decision:** A single HTML frontend is included in Phase 1 
scope covering both document upload and query interaction.
**Reason:** Without a UI the project cannot be demoed 
effectively. The demo must show the complete end-to-end 
story — a lawyer uploading a contract and a lawyer querying 
it — not just one half. A JSON response in Postman does not 
demonstrate business value. The frontend has two distinct 
views: an upload tab where a lawyer selects a PDF, inputs 
matter ID and document type, and uploads via pre-signed S3 
URL; and a query tab where a lawyer types a question, 
optionally filters by matter, and receives an answer with 
source citations.
**Implementation:** Single self-contained HTML file with 
two tabs. Upload tab generates a pre-signed S3 URL via 
API Gateway and uploads directly to S3 from the browser. 
Query tab calls the query Lambda via API Gateway and 
displays the answer and citations. Runs locally for demo.
**Phase 2:** Host via S3 static website with CloudFront 
distribution for production deployment and public access.
**Outcome:** Demo-ready frontend covering both upload and 
query flows included in Phase 1.