# Test Data Manifest

This document defines the seven documents used to populate the 
Vandermeer & Associates knowledge base for testing and demo purposes.
All documents are synthetic and generated for demo use only.

---

## Document Library

| # | Document | Matter ID | Document Type | Uploaded By | Year |
|---|---|---|---|---|---|
| 1 | Accenture Supply Agreement | `accenture-supply-2023` | contracts | Sophie van der Berg | 2023 |
| 2 | Accenture NDA | `accenture-supply-2023` | contracts | Nathaniel Kay | 2026 |
| 3 | Senior Associate Employment Contract | `hr-employment-2022` | contracts | Sophie van der Berg | 2022 |
| 4 | ASML Litigation Filing | `asml-litigation-2024` | filings | James Harrington | 2024 |
| 5 | Legal Opinion — Data Processing | `asml-litigation-2024` | opinions | Lena Kaufmann | 2024 |
| 6 | Corporate Governance Report | `corporate-governance-2021` | reports | Sophie van der Berg | 2021 |
| 7 | Dutch Supply Agreement | `dutch-supply-2023` | contracts | Lena Kaufmann | 2023 |

---

## S3 Folder Path Convention

Documents are uploaded following this path structure:
matters/<matter-id>/<document-type>/<uploader-name>/<filename.pdf>

**Examples:**
matters/accenture-supply-2023/contracts/sophie-van-der-berg/accenture-supply-agreement.pdf
matters/accenture-supply-2023/contracts/nathaniel-kay/accenture-nda.pdf
matters/hr-employment-2022/contracts/sophie-van-der-berg/senior-associate-employment.pdf
matters/asml-litigation-2024/filings/james-harrington/asml-litigation-filing.pdf
matters/asml-litigation-2024/opinions/lena-kaufmann/legal-opinion-data-processing.pdf
matters/corporate-governance-2021/reports/sophie-van-der-berg/corporate-governance-report.pdf
matters/dutch-supply-2023/contracts/lena-kaufmann/dutch-supply-agreement.pdf

---

## Query-to-Document Mapping

| Query | Matter Filter | Documents Expected in Results |
|---|---|---|
| Termination clauses in Accenture supply matter | `accenture-supply-2023` | Doc 1, Doc 2 |
| Automatic renewal provisions across all contracts | None | Doc 1, Doc 3, Doc 7 |
| Key liability limitations across all contracts | None | Doc 1, Doc 2, Doc 3, Doc 5, Doc 7 |
| Payment terms | None | Doc 7 |
| Criminal liability clauses | None | No results — expected |

---

## Lawyer Directory

| Name | Role | Documents Uploaded |
|---|---|---|
| Sophie van der Berg | Partner | Doc 1, Doc 3, Doc 6 |
| James Harrington | Senior Associate | Doc 4 |
| Lena Kaufmann | Associate | Doc 5, Doc 7 |