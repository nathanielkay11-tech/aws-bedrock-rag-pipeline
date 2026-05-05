# AWS Bedrock RAG Pipeline

> This is the third project in my AWS portfolio. While my
> [previous project](https://github.com/nathanielkay11-tech/aws-ai-document-pipeline)
> built a serverless AI document processing pipeline, this one adds a
> retrieval layer on top of Bedrock — moving from "I can make infrastructure
> intelligent" to "I can make infrastructure answer questions."

> 🚧 **Work in Progress** — This project is actively being built and
> documented. Architecture decisions, cost analysis and testing results
> will be added as each iteration completes.

---

## 🗺️ Project Navigation: The 3 Iterations

### 📍 Iteration 1: Architecture Design and ADRs
- **What it is:** The architecture design phase. See
  [`/docs/design-decisions.md`](./docs/design-decisions.md) for all
  architectural decision records covering service selection, vector store
  choice, and security design.
- **The Goal:** To design a production-quality RAG system from first
  principles — defining the retrieval strategy, chunking approach, and
  query architecture before writing a single line of code.
- **Status:** 🔄 In progress

### 📍 Iteration 2: Infrastructure Build and Testing
- **What it is:** Full Terraform IaC deployment of all AWS services,
  Lambda query handler development, and end-to-end testing across
  multiple query types and document sets.
- **The Goal:** To prove the architecture works in a real AWS environment
  — query accuracy, citation quality, and latency documented with
  evidence in [`/docs/testing-log.md`](./docs/testing-log.md).
- **Status:** 🔄 Not started

### 📍 Iteration 3: One-Shot Prompt Engineering
- **What it is:** A single, multi-constraint prompt capable of
  reproducing the complete Terraform infrastructure and Lambda function
  from scratch in one AI-assisted pass.
- **The Goal:** To demonstrate prompt engineering maturity — treating
  the AI as a junior engineer and validating every output as the
  architect.
- **Status:** 🔄 Not started

---

## 🏢 The Business Problem

European legal and procurement teams manage hundreds of contracts
simultaneously. Finding a specific clause — a liability cap, a
termination right, a renewal date — requires a lawyer to manually
open and read each document. At €250–400/hour for legal associate
time, this is expensive, slow, and doesn't scale.

This project automates that search layer. A question goes in.
A precise answer with source citations comes out — directly referencing
the relevant clause in the relevant document, without a human reading
through the entire contract library first.

---

## 💡 Why This Architecture — Design Decisions & Cost Analysis

### Architecture Alternatives Considered

Three approaches were evaluated before settling on the current design:

**Option 1: Fine-tuned foundation model (Rejected)**
Training a model on legal documents would produce a system with broad
knowledge of contract language but no ability to answer questions about
specific documents it wasn't trained on. Every new contract added would
require retraining. This fundamentally mismatches the use case — legal
teams need answers about their specific contracts, not general legal
knowledge.

**Option 2: Direct Bedrock invocation with documents in context (Rejected)**
Passing entire contract PDFs directly into a Bedrock prompt works for
single documents but breaks at scale. Large contracts exceed context
windows. Multiple documents simultaneously make costs prohibitive and
accuracy degrades as context grows. This approach doesn't scale beyond
a handful of short documents.

**Option 3: RAG with Bedrock Knowledge Bases — Current Architecture ✅**
Knowledge Bases handles chunking, embedding, and vector storage
automatically. At query time, only the relevant document chunks are
retrieved and passed to the model — keeping context lean, costs low,
and accuracy high regardless of how many documents are in the knowledge
base. The system scales from 10 contracts to 10,000 without
architectural changes.

---

### 📊 Projected Cost by Use Case Tier

#### Volume Definitions

| Tier | Monthly Queries | Organisation Profile |
| --- | --- | --- |
| 🟢 **Small** | 500–2,000 | Boutique law firm or startup in-house legal team |
| 🟡 **Mid-size** | 5,000–20,000 | Regional law firm or scale-up legal department |
| 🔴 **Large** | 50,000–200,000 | Magic Circle firm or multinational legal function |

---

#### Monthly Cost Estimates

All figures based on current AWS eu-west-1 pricing (May 2026). Assumes
average query generates ~1,500 input tokens and ~500 output tokens,
with 5 document chunks retrieved per query.

| Service | Small (2,000/mo) | Mid (20,000/mo) | Large (200,000/mo) |
| --- | --- | --- | --- |
| Amazon Bedrock (Claude Sonnet) | ~€5 | ~€40 | ~€350 |
| OpenSearch Serverless | ~€25 | ~€25 | ~€80 |
| AWS Lambda | <€1 | ~€2 | ~€15 |
| Amazon API Gateway | <€1 | ~€1 | ~€8 |
| Amazon S3 | <€1 | <€1 | ~€5 |
| CloudWatch Logs | <€1 | ~€2 | ~€10 |
| **Total Monthly** | **~€32** | **~€71** | **~€468** |
| **Cost per query** | **~€0.016** | **~€0.004** | **~€0.002** |

> ⚠️ These are indicative estimates. Bedrock token usage will vary
> based on query complexity and document length. Always validate with
> the [AWS Pricing Calculator](https://calculator.aws/pricing/2/home)
> for production budgeting.

---

#### Cost vs. Manual Review Benchmark

European legal associate rates: €250–400/hour. Average time to manually
locate and extract a specific clause across a contract library: 20–30
minutes per query.

| Volume | Manual Review Cost | Pipeline Cost | Saving |
| --- | --- | --- | --- |
| 2,000 queries/month | ~€17,000 | ~€32 | **99.8%** |
| 20,000 queries/month | ~€170,000 | ~€71 | **99.9%** |
| 200,000 queries/month | ~€1,700,000 | ~€468 | **99.9%** |

The pipeline doesn't replace legal judgement — complex contract
interpretation still requires a lawyer. It eliminates the document
search layer entirely, freeing legal staff to focus on analysis
rather than retrieval.

---

## 🏗️ Architecture Overview

```mermaid
graph LR
    A[Legal Contract PDFs] --> B[Amazon S3]
    B -->|S3 ObjectCreated event| C[Ingestion Lambda]
    C -->|start_ingestion_job| D[Bedrock Knowledge Base]
    D --> E[OpenSearch Serverless]
    F[User Query] --> G[Amazon API Gateway]
    G --> H[Query Lambda]
    H -->|RetrieveAndGenerate| D
    D --> I[Amazon Bedrock Claude]
    I --> J[Answer + Source Citations]
```

---

## 🚀 Project Status

🔄 Iteration 1 in progress — architecture design and ADRs

---

## 🎬 Demo Video

*Coming in Iteration 2*

---

## ✅ Testing Results

*Coming in Iteration 2*

---

## ⚠️ Known Limitations

*To be documented as the build progresses*

---

## 🤖 Development Approach

This project was developed using an AI-assisted workflow. Claude
(Anthropic) was used as a technical sounding board throughout the
build — helping with code structure, troubleshooting, and
documentation. All architectural decisions, business logic,
security considerations and project direction were driven by me.

This reflects how modern cloud engineers actually work in 2026 —
knowing how to leverage AI tools effectively is itself a
professional skill.