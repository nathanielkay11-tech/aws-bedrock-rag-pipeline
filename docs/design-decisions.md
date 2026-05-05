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