-- ============================================================================
-- QARABA CARE: REFORMED DATABASE SCHEMA & PEDIGREE GRAPH ARCHITECTURE
-- Target Engine: PostgreSQL 15+ (ADHICS v2 & UAE PDPL Compliant)
-- Standards: HL7 FHIR R4 Genomics & GA4GH Pedigree Specification
-- Ready for GitHub Repository Deployment
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. ENUMERATED TYPES FOR CLINICAL & GENOMIC STANDARDIZATION
CREATE TYPE biological_sex_enum AS ENUM ('MALE', 'FEMALE', 'UNKNOWN');
CREATE TYPE acmg_classification_enum AS ENUM (
    'PATHOGENIC',
    'LIKELY_PATHOGENIC',
    'VUS',
    'LIKELY_BENIGN',
    'BENIGN'
);
CREATE TYPE zygosity_enum AS ENUM ('HETEROZYGOUS', 'HOMOZYGOUS_ALT', 'HEMIZYGOUS', 'WILDTYPE');
CREATE TYPE risk_tier_enum AS ENUM ('TIER_1_STANDARD', 'TIER_2_ELEVATED', 'TIER_3_HIGH_CONSANGUINITY', 'TIER_4_SHARED_CARRIER');
CREATE TYPE reproductive_pathway_enum AS ENUM (
    'ROUTINE_CLEARANCE',
    'EXPANDED_CARRIER_SEQUENCING',
    'IVF_PGT_M_REFERRAL',
    'PRENATAL_DIAGNOSTIC_CVS_AMNIO',
    'CASCADE_FAMILY_SCREENING'
);

-- ============================================================================
-- 2. DYNAMIC CONSENT & CRYPTOGRAPHIC IDENTITY ISOLATION TABLE
-- Separates National ID / UAE Pass PII from clinical pedigree graphs
-- ============================================================================
CREATE TABLE consent_tokens (
    consent_token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    national_id_sha256 CHAR(64) NOT NULL UNIQUE,
    consent_scope JSONB NOT NULL DEFAULT '{"pedigree_sharing": true, "partner_match": true, "anonymous_cascade": true}',
    signed_by_proband_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ NULL,
    data_residency_region VARCHAR(32) NOT NULL DEFAULT 'UAE-NORTH-AZ1'
);

-- ============================================================================
-- 3. PATIENT PROBAND & EXTENDED FAMILY NODE TABLE (GRAPH VERTICES)
-- Represents both active clinic patients (probands) and ancestral family nodes
-- ============================================================================
CREATE TABLE pedigree_nodes (
    node_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consent_token_id UUID NULL REFERENCES consent_tokens(consent_token_id) ON DELETE SET NULL,
    is_index_proband BOOLEAN NOT NULL DEFAULT FALSE,
    display_alias VARCHAR(64) NOT NULL, -- e.g., "Paternal Grandfather (PGF-1)"
    biological_sex biological_sex_enum NOT NULL,
    birth_year SMALLINT NULL,
    is_deceased BOOLEAN NOT NULL DEFAULT FALSE,
    tribal_or_geographic_origin VARCHAR(120) NULL,
    reported_phenotypes_hpo TEXT[] DEFAULT '{}', -- Human Phenotype Ontology codes e.g. {'HP:0001903'}
    runs_of_homozygosity_froh NUMERIC(6,5) NULL, -- Lab-measured genomic inbreeding coefficient
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pedigree_nodes_proband ON pedigree_nodes(is_index_proband);

-- ============================================================================
-- 4. PEDIGREE DIRECTED ACYCLIC GRAPH (DAG) EDGES TABLE
-- Enables millisecond traversal of multi-generational consanguineous loops
-- ============================================================================
CREATE TABLE pedigree_graph_edges (
    edge_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_graph_id UUID NOT NULL,
    parent_node_id UUID NOT NULL REFERENCES pedigree_nodes(node_id) ON DELETE CASCADE,
    child_node_id UUID NOT NULL REFERENCES pedigree_nodes(node_id) ON DELETE CASCADE,
    relationship_confidence NUMERIC(3,2) NOT NULL DEFAULT 1.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_parent_child_edge UNIQUE (family_graph_id, parent_node_id, child_node_id),
    CONSTRAINT chk_no_self_loop CHECK (parent_node_id <> child_node_id)
);

CREATE INDEX idx_pedigree_edges_graph ON pedigree_graph_edges(family_graph_id);
CREATE INDEX idx_pedigree_edges_parent ON pedigree_graph_edges(parent_node_id);
CREATE INDEX idx_pedigree_edges_child ON pedigree_graph_edges(child_node_id);

-- ============================================================================
-- 5. PREMARITAL COUPLE MATCH & KINSHIP CALCULATION CASE TABLE
-- Stores deterministic Wright's Path Coefficient (R and F) outputs
-- ============================================================================
CREATE TABLE couple_match_cases (
    case_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_graph_id UUID NOT NULL,
    partner_a_node_id UUID NOT NULL REFERENCES pedigree_nodes(node_id),
    partner_b_node_id UUID NOT NULL REFERENCES pedigree_nodes(node_id),
    common_ancestors_count SMALLINT NOT NULL DEFAULT 0,
    wright_relationship_coeff_r NUMERIC(8,6) NOT NULL DEFAULT 0.000000,
    offspring_inbreeding_coeff_f NUMERIC(8,6) NOT NULL DEFAULT 0.000000,
    kinship_description_en VARCHAR(128) NOT NULL,
    kinship_description_ar VARCHAR(128) NOT NULL,
    assigned_risk_tier risk_tier_enum NOT NULL DEFAULT 'TIER_1_STANDARD',
    intake_duration_seconds INTEGER NOT NULL DEFAULT 420,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_distinct_partners CHECK (partner_a_node_id <> partner_b_node_id)
);

-- ============================================================================
-- 6. MOLECULAR LABORATORY ORDERS & ACMG CARRIER VARIANT CALLS (HL7 FHIR R4)
-- ============================================================================
CREATE TABLE carrier_variant_calls (
    variant_call_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL REFERENCES pedigree_nodes(node_id) ON DELETE CASCADE,
    fhir_diagnostic_report_id VARCHAR(128) NOT NULL,
    gene_symbol VARCHAR(32) NOT NULL,          -- e.g., 'HBB', 'SMN1', 'CFTR', 'G6PD'
    transcript_hgvs_c VARCHAR(128) NOT NULL,   -- e.g., 'NM_000518.5:c.118C>T'
    protein_hgvs_p VARCHAR(128) NULL,          -- e.g., 'p.Gln40Ter'
    condition_name VARCHAR(160) NOT NULL,      -- e.g., 'Beta-Thalassemia Major'
    inheritance_mode VARCHAR(32) NOT NULL DEFAULT 'AUTOSOMAL_RECESSIVE',
    zygosity zygosity_enum NOT NULL,
    acmg_classification acmg_classification_enum NOT NULL,
    mena_allele_frequency NUMERIC(8,7) NULL,
    sequenced_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_variant_node_gene ON carrier_variant_calls(node_id, gene_symbol);

-- ============================================================================
-- 7. GENETIC COUNSELOR COPILOT & HUMAN-IN-THE-LOOP SIGN-OFF TABLE
-- Enforces mandatory clinician verification before releasing high-risk reports
-- ============================================================================
CREATE TABLE counseling_decision_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES couple_match_cases(case_id) ON DELETE CASCADE,
    shared_pathogenic_genes TEXT[] DEFAULT '{}',
    mendelian_offspring_risk_pct NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    recommended_pathway reproductive_pathway_enum NOT NULL,
    bilingual_summary_en TEXT NOT NULL,
    bilingual_summary_ar TEXT NOT NULL,
    cascade_screening_invite_token CHAR(32) UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
    counselor_license_number VARCHAR(64) NOT NULL,
    counselor_signed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 8. analytical VIEW: COUPLE SHARED PATHOGENIC CARRIER MATRIX
-- Automatically detects couples carrying pathogenic variants in the same gene
-- ============================================================================
CREATE OR REPLACE VIEW vw_couple_shared_carrier_alerts AS
SELECT 
    c.case_id,
    c.offspring_inbreeding_coeff_f,
    c.kinship_description_en,
    va.gene_symbol,
    va.condition_name,
    va.transcript_hgvs_c AS partner_a_variant,
    vb.transcript_hgvs_c AS partner_b_variant,
    va.acmg_classification AS partner_a_acmg,
    vb.acmg_classification AS partner_b_acmg,
    CASE 
        WHEN va.inheritance_mode = 'AUTOSOMAL_RECESSIVE' THEN 25.00
        ELSE 50.00
    END AS offspring_affected_probability_pct
FROM couple_match_cases c
JOIN carrier_variant_calls va ON c.partner_a_node_id = va.node_id
JOIN carrier_variant_calls vb ON c.partner_b_node_id = vb.node_id
    AND va.gene_symbol = vb.gene_symbol
WHERE va.acmg_classification IN ('PATHOGENIC', 'LIKELY_PATHOGENIC')
  AND vb.acmg_classification IN ('PATHOGENIC', 'LIKELY_PATHOGENIC');