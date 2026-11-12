# 🧬 Qaraba Care (قرابة كير)
**AI-Driven Consanguinity Pedigree & Premarital Genomic Risk Intelligence Platform**  
*Official Solo-Founder Submission for the Future Health Digital Innovation Challenge (Abu Dhabi)*

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](https://opensource.org/licenses/MIT)
[![Standard: HL7 FHIR R4](https://img.shields.io/badge/Interoperability-HL7%20FHIR%20R4-blue.svg)](https://hl7.org/fhir/genomics.html)
[![Standard: GA4GH Pedigree](https://img.shields.io/badge/Standard-GA4GH%20Pedigree-6b5b4e.svg)](https://www.ga4gh.org/)
[![Compliance: ADHICS v2 & UAE PDPL](https://img.shields.io/badge/Compliance-ADHICS%20v2%20%7C%20UAE%20PDPL-success.svg)](#security--regulatory-compliance)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![PostgreSQL 15+](https://img.shields.io/badge/PostgreSQL-15%2B-336791.svg)](https://www.postgresql.org/)

---

## 📌 Overview & Problem Statement

Across the Middle East and North Africa (MENA) region, consanguineous unions account for **25% to 60% of all marriages**, contributing to a 5- to 12-fold increase in severe autosomal recessive conditions (such as Beta-Thalassemia Major, Spinal Muscular Atrophy, Cystic Fibrosis, and inborn errors of metabolism) costing regional health systems over **$4.2 Billion annually**.

Despite mandatory premarital screening programs in the UAE, Saudi Arabia, and Egypt, current clinical workflows suffer from three critical bottlenecks:
1. **Manual Paper Pedigrees:** Genetic counselors spend **45 minutes per couple** drawing family trees by hand, missing complex multi-generational cousin loops.
2. **Siloed Basic Blood Panels:** Routine hemoglobinopathy screening misses silent single-gene carriers (e.g., *SMN1* copy-number deletions in SMA), while static PDF lab reports cannot trigger automated cross-family alerts in hospital EHRs.
3. **Delayed Triage:** Counseling waitlists stretch **6 to 14 weeks**, often identifying high-risk couples only *after* the birth of an affected child.

**Qaraba Care** transforms premarital screening from a reactive, paper-based bottleneck into a proactive, 4-stage digital genomic and pedigree intelligence pipeline.

---

## 🚀 Key Platform Capabilities

* **🗣️ Stage 1: Bilingual Citizen Onboarding (< 8 Minutes)**  
  Culturally sensitive Arabic/English conversational wizard that guides engaged couples through building a 4-generation family pedigree prior to clinic arrival—cutting clinical intake time by **80%**.
* **📐 Stage 2: Deterministic Kinship Graph Engine (< 4 ms Execution)**  
  Zero "black-box" generative AI is used for medical risk math. Family trees are modeled as Directed Acyclic Graphs (DAGs) to compute exact **Sewall Wright’s Coefficient of Relationship ($R$)** and **Offspring Coefficient of Inbreeding ($F$)** across arbitrary multi-generational cousin loops:
  $$F_I = \sum \left(\frac{1}{2}\right)^{n_1 + n_2 + 1} (1 + F_A)$$
* **🧪 Stage 3: HL7 FHIR R4 Lab & ACMG Variant Matching**  
  Ingests sequencing calls from accredited molecular labs, cross-matching Partner A and Partner B alleles against **MENA reference cohorts** (Arab Variome, CTGA, Emirati Genome baselines) to detect shared Class 4/5 pathogenic variants and calculate Bayesian residual carrier risks.
* **👩‍⚕️ Stage 4: Human-in-the-Loop Counselor Copilot & Cascade Screening**  
  Drafts bilingual consultation action plans (IVF with PGT-M, prenatal diagnostics, or anonymous tokenized cascade screening invites for unmarried siblings) requiring mandatory electronic sign-off by a licensed genetic counselor.

---

## 📂 Repository Structure

```text
qaraba-care/
├── README.md                                     # Project documentation & quick-start guide
├── schema.sql                                    # Reformed PostgreSQL + DAG Pedigree ERD Schema
├── risk_engine.py                                # Python/FastAPI Kinship (Wright's F) & Carrier Engine
├── pitch_studio.html                             # Interactive Browser Video/Voiceover Recording Studio
├── docs/
│   ├── qaraba_care_project_plan.pdf              # Master Project Plan, Workflow Diagrams & 5-Yr Financials
│   ├── qaraba_care_feasibility_study.pdf         # Technical, Legal, Operational & Economic Feasibility
│   ├── Future_Health_Deck_Qaraba_Care.md         # 16-Slide Future Health Challenge Submission Content
│   └── Presentation_Video_Script_and_Audio.md    # Time-coded 3-minute pitch script & FFmpeg guide
```

---

## ⚡ Quick Start & Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/qaraba-care.git
cd qaraba-care
```

### 2. Run the Standalone CLI Kinship & Genomic Benchmark (Zero Dependencies Required)
`risk_engine.py` includes a built-in validation benchmark for our clinical demo couple (**Tariq & Laila**, Double First Cousins with shared *HBB* and *SMN1* carrier variants) that runs in pure Python 3:
```bash
python risk_engine.py
```

**Expected CLI Output:**
```json
{
  "partner_a_id": "PROBAND_TARIQ",
  "partner_b_id": "PROBAND_LAILA",
  "wright_relationship_coefficient_R": 0.25,
  "offspring_inbreeding_coefficient_F": 0.125,
  "offspring_autozygosity_pct": 12.5,
  "kinship_label_en": "Double First Cousins / Equivalent High Consanguinity",
  "kinship_label_ar": "أبناء عمومة وخؤولة مزدوجين (قرابة من الدرجة العالية)",
  "assigned_risk_tier": "TIER_3_HIGH_CONSANGUINITY",
  "recommended_clinical_pathway": "Mandatory Expanded Carrier Screening (420+ Gene NGS Panel + SMA MLPA)"
}
```

### 3. Launch the FastAPI Microservice (Optional)
```bash
pip install fastapi uvicorn pydantic
uvicorn risk_engine:app --reload --port 8000
```
* Open `http://127.0.0.1:8000/docs` to test the interactive Swagger UI API, or query `GET /api/v1/demo-couple-assessment`.

### 4. Initialize the Reformed PostgreSQL Database Schema
```bash
psql -U postgres -d qaraba_care_db -f schema.sql
```

---

## 🔑 Judge Sandbox & Guest Demo Access

In accordance with the **Future Health Digital Innovation Challenge** guidelines:
* **One-Click Guest Mode:** Judges can open the web application or run `/api/v1/demo-couple-assessment` to immediately inspect the pre-loaded consanguineous couple case (**Tariq & Laila**) without login barriers.
* **Role-Based Sandbox Credentials:**
  * **Genetic Counselor Portal:** `judge.counselor@qarabacare.ae` | Password: `FutureHealth2026!`
  * **Couple Onboarding View:** `demo.couple@qarabacare.ae` | Password: `FutureHealth2026!`

---

## 🛡️ Security, Privacy & Regulatory Compliance

* **Compartmented Pedigree Graph Visibility:** Each partner can only view their own family branch until mutual cryptographic consent (`consent_tokens`) is signed.
* **Identity Isolation:** National IDs / UAE Pass identifiers are salted and hashed via `SHA-256` (`pgcrypto`), decoupling PII from clinical graph vertices.
* **Data Sovereignty:** Architected for 100% in-country hosting on **Microsoft Azure UAE North**, compliant with **Abu Dhabi Healthcare Information and Cyber Security Standard (ADHICS v2)**, **Malaffi**, **NABIDH**, and **UAE Federal Personal Data Protection Law (PDPL Law No. 45 of 2021)**.

---

## 📈 5-Year Health-Economic Impact

* **Break-Even Milestone:** Month 19 (Hybrid B2G SaaS at $14/couple + B2B IVF/Lab API licensing)
* **5-Year Commercial NPV (10% discount rate):** **$5.42 Million** (IRR: **68.4%**)
* **Public Health ROI:** **$6.40 saved** in avoided lifetime pediatric hospitalization and orphan drug expenditure for every **$1.00 invested** ($72.1M cumulative 5-year savings across 898,000 screened couples).

---

## 👤 Solo Founder & Architect

* **Meeda** — *Founder, Health Informatics & AI System Architect (Egypt / UAE)*  
* **Conflict of Interest Declaration:** None declared with Future Health Digital Innovation Challenge organizers, Hack2Skill, Microsoft, Inception (G42), or MBZUAI.