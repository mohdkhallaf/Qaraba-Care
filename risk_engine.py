"""
Qaraba Care — Consanguinity Pedigree Graph, Carrier Risk & AI Counselor Copilot Engine
======================================================================================
Solo Founder & Architect: Meeda | Future Health Digital Innovation Challenge 2026

Features:
1. Directed Acyclic Graph (DAG) representation of multi-generational family pedigrees.
2. Deterministic calculation of Sewall Wright's Coefficient of Relationship (R) and
   Offspring Coefficient of Inbreeding (F), handling double first cousins and ancestral loops.
3. Multi-gene MENA autosomal recessive risk mapper incorporating family history HPO flags.
4. Working AI Counselor Copilot synthesizer generating bilingual (Arabic/English) plain-language
   risk explanations, tailored preconception steps, certified genetic counselor referrals,
   and mandatory clinical boundary disclaimers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import json

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


MENA_CARRIER_PRIORS: Dict[str, Dict[str, float | str]] = {
    "HBB": {
        "condition": "Beta-Thalassemia Major / Sickle Cell Disease",
        "carrier_freq": 0.045,
        "panel_sensitivity": 0.992,
    },
    "SMN1": {
        "condition": "Spinal Muscular Atrophy (SMA)",
        "carrier_freq": 0.025,
        "panel_sensitivity": 0.960,
    },
    "GJB2": {
        "condition": "Autosomal Recessive Nonsyndromic Hearing Loss",
        "carrier_freq": 0.032,
        "panel_sensitivity": 0.985,
    },
    "CFTR": {
        "condition": "Cystic Fibrosis",
        "carrier_freq": 0.018,
        "panel_sensitivity": 0.975,
    },
}


@dataclass
class PedigreeNode:
    node_id: str
    name: str
    sex: str
    parents: List[str] = field(default_factory=list)
    reported_conditions: List[str] = field(default_factory=list)


class ConsanguinityGraphEngine:
    """
    Computes exact Sewall Wright's Coefficient of Inbreeding (F) and Relationship (R)
    over multi-generational pedigrees with arbitrary cousin loops.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, PedigreeNode] = {}
        self._inbreeding_cache: Dict[str, float] = {}

    def add_individual(
        self,
        node_id: str,
        name: str,
        sex: str,
        parents: Optional[List[str]] = None,
        reported_conditions: Optional[List[str]] = None,
    ) -> None:
        self.nodes[node_id] = PedigreeNode(
            node_id=node_id,
            name=name,
            sex=sex,
            parents=parents or [],
            reported_conditions=reported_conditions or [],
        )
        self._inbreeding_cache.clear()

    def get_all_ancestral_paths(
        self, start_id: str, max_depth: int = 8
    ) -> Dict[str, List[List[str]]]:
        paths_by_ancestor: Dict[str, List[List[str]]] = {}
        queue: List[List[str]] = [[start_id]]

        while queue:
            current_path = queue.pop(0)
            current_id = current_path[-1]
            if len(current_path) - 1 >= max_depth:
                continue

            node = self.nodes.get(current_id)
            if not node:
                continue

            for parent_id in node.parents:
                if parent_id in current_path:
                    continue
                new_path = current_path + [parent_id]
                paths_by_ancestor.setdefault(parent_id, []).append(new_path)
                queue.append(new_path)

        return paths_by_ancestor

    def compute_individual_inbreeding_f(self, node_id: str) -> float:
        if node_id in self._inbreeding_cache:
            return self._inbreeding_cache[node_id]

        node = self.nodes.get(node_id)
        if not node or len(node.parents) < 2:
            self._inbreeding_cache[node_id] = 0.0
            return 0.0

        p1, p2 = node.parents[0], node.parents[1]
        f_val = self.compute_hypothetical_offspring_f(p1, p2)
        self._inbreeding_cache[node_id] = f_val
        return f_val

    def compute_hypothetical_offspring_f(self, partner_a_id: str, partner_b_id: str) -> float:
        if partner_a_id == partner_b_id:
            return 0.5

        paths_a = self.get_all_ancestral_paths(partner_a_id)
        paths_b = self.get_all_ancestral_paths(partner_b_id)

        common_ancestors = set(paths_a.keys()).intersection(set(paths_b.keys()))
        total_f = 0.0

        for ancestor_id in common_ancestors:
            f_ancestor = self.compute_individual_inbreeding_f(ancestor_id)
            for path_1 in paths_a[ancestor_id]:
                for path_2 in paths_b[ancestor_id]:
                    interior_1 = set(path_1[:-1])
                    interior_2 = set(path_2[:-1])
                    if interior_1.isdisjoint(interior_2):
                        n1 = len(path_1) - 1
                        n2 = len(path_2) - 1
                        total_f += (0.5 ** (n1 + n2 + 1)) * (1.0 + f_ancestor)

        return round(total_f, 6)


def generate_ai_counselor_copilot_plan(
    male_name: str,
    female_name: str,
    relationship_label: str,
    r_coeff: float,
    f_coeff: float,
    target_gene: str,
    offspring_risk: float,
) -> Dict[str, str]:
    """
    Synthesizes plain-language bilingual risk explanations, preconception action steps,
    certified genetic counselor referral pathways, and explicit clinical disclaimers.
    """
    pct_str = f"{offspring_risk * 100:.2f}%"
    condition_name = str(MENA_CARRIER_PRIORS.get(target_gene, {}).get("condition", target_gene))

    explanation_en = (
        f"Plain-Language Summary for {male_name} & {female_name}: Based on your family tree "
        f"topology ({relationship_label}, R = {r_coeff:.4f}, Offspring F = {f_coeff:.4f}), "
        f"our educational risk mapper estimates a {pct_str} probability per pregnancy for "
        f"{condition_name} ({target_gene}). Recommended Preconception Steps: (1) Review confirmatory "
        f"molecular carrier sequencing (NGS/MLPA); (2) Discuss Pre-implantation Genetic Testing "
        f"for Monogenic Disorders (PGT-M / IVF) or prenatal diagnostic options with a certified "
        f"genetic counselor."
    )

    explanation_ar = (
        f"ملخص تثقيفي مبسط للشريكين ({male_name} و {female_name}): بناءً على تحليل شجرة العائلة "
        f"({relationship_label}، معامل القرابة R = {r_coeff:.4f}، معامل زواج الأقارب F = {f_coeff:.4f})، "
        f"تبلغ النسبة التقديرية لاحتمالية الإصابة بحالة ({condition_name}) نحو {pct_str} في كل حمل. "
        f"الخطوات الوقائية الموصى بها: مراجعة أخصائي المشورة الوراثية المعتمد لمناقشة الفحص الجيني التأكيدي "
        f"وخيارات الفحص الوراثي للأجنة قبل الغرس (PGT-M)."
    )

    return {
        "plain_language_explanation_en": explanation_en,
        "plain_language_explanation_ar": explanation_ar,
        "certified_referral_pathway": "Sheikh Shakhbout Medical City (SSMC) / Cleveland Clinic Abu Dhabi Genetics Board (via Malaffi FHIR R4)",
        "clinical_boundary_disclaimer": (
            "EDUCATIONAL RISK STRATIFICATION ONLY — NOT A DEFINITIVE MEDICAL DIAGNOSIS. "
            "All reproductive decisions require accredited laboratory confirmation and consultation "
            "with a certified healthcare professional."
        ),
    }


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Qaraba Care — Interactive Pedigree & AI Counselor Copilot API",
        version="2.5.0",
        description="Deterministic Consanguinity Graph Math, Multi-Gene Carrier Mapper & Bilingual AI Copilot",
    )

    class CoupleEvaluationRequest(BaseModel):
        male_name: str = Field("Tariq Al-Mansoori", example="Tariq Al-Mansoori")
        female_name: str = Field("Laila Al-Mansoori", example="Laila Al-Mansoori")
        relationship_type: str = Field("first_cousin", example="first_cousin")
        secondary_ancestral_loop: bool = Field(False, description="Adds F_A = 0.0625 loop")
        target_gene: str = Field("HBB", example="HBB")
        male_carrier_status: str = Field("confirmed", example="confirmed")
        female_carrier_status: str = Field("confirmed", example="confirmed")
        positive_family_history: bool = Field(True, description="Positive family HPO phenotype flag")

    @app.get("/")
    def health_check() -> Dict[str, str]:
        return {
            "status": "online",
            "service": "Qaraba Care Risk & AI Copilot Engine",
            "version": "2.5.0",
            "disclaimer": "Educational Risk Stratification — Not a Definitive Medical Diagnosis",
        }

    @app.post("/api/v1/calculate-risk")
    def calculate_couple_risk(req: CoupleEvaluationRequest) -> Dict[str, object]:
        t0 = time.perf_counter()
        topology_map = {
            "double_first": {"R": 0.2500, "label": "Double First Cousins"},
            "first_cousin": {"R": 0.1250, "label": "First Cousins"},
            "first_once_removed": {"R": 0.0625, "label": "First Cousins Once Removed"},
            "second_cousin": {"R": 0.03125, "label": "Second Cousins"},
            "distant_tribal": {"R": 0.0078125, "label": "Distant Tribal Kinship"},
            "unrelated": {"R": 0.0, "label": "Unrelated"},
        }
        topo = topology_map.get(req.relationship_type, topology_map["first_cousin"])
        fa = 0.0625 if (req.secondary_ancestral_loop and topo["R"] > 0) else 0.0
        r_val = round(float(topo["R"]) * (1.0 + fa), 6)
        f_val = round(r_val / 2.0, 6)

        prior = float(MENA_CARRIER_PRIORS.get(req.target_gene, {"carrier_freq": 0.03})["carrier_freq"])
        if req.positive_family_history:
            prior = min(0.25, prior * 2.5)

        if req.male_carrier_status == "negative" and req.female_carrier_status == "negative":
            p_affected = 0.00005
        elif req.male_carrier_status == "confirmed" and req.female_carrier_status == "confirmed":
            p_affected = 0.25
        elif req.male_carrier_status == "confirmed" or req.female_carrier_status == "confirmed":
            p_affected = 0.25 * min(0.95, r_val + (1.0 - r_val) * prior)
        else:
            q = prior / 2.0
            p_affected = (q * q) * (1.0 - f_val) + q * f_val

        copilot = generate_ai_counselor_copilot_plan(
            male_name=req.male_name,
            female_name=req.female_name,
            relationship_label=str(topo["label"]),
            r_coeff=r_val,
            f_coeff=f_val,
            target_gene=req.target_gene,
            offspring_risk=p_affected,
        )

        return {
            "Wright_R": r_val,
            "Offspring_F": f_val,
            "target_gene": req.target_gene,
            "offspring_affected_probability": round(p_affected, 5),
            "computation_ms": round((time.perf_counter() - t0) * 1000, 3),
            "ai_counselor_copilot": copilot,
        }


if __name__ == "__main__":
    engine = ConsanguinityGraphEngine()
    engine.add_individual("GP1", "Grandfather", "M")
    engine.add_individual("GP2", "Grandmother", "F")
    engine.add_individual("FATHER_A", "Father A", "M", parents=["GP1", "GP2"])
    engine.add_individual("FATHER_B", "Father B", "M", parents=["GP1", "GP2"])
    engine.add_individual("MOTHER_A", "Mother A", "F")
    engine.add_individual("MOTHER_B", "Mother B", "F")
    engine.add_individual("TARIQ", "Tariq Al-Mansoori", "M", parents=["FATHER_A", "MOTHER_A"])
    engine.add_individual("LAILA", "Laila Al-Mansoori", "F", parents=["FATHER_B", "MOTHER_B"])

    f_score = engine.compute_hypothetical_offspring_f("TARIQ", "LAILA")
    r_score = 2.0 * f_score
    copilot_out = generate_ai_counselor_copilot_plan(
        "Tariq Al-Mansoori", "Laila Al-Mansoori", "First Cousins", r_score, f_score, "HBB", 0.25
    )
    print(json.dumps({"R": r_score, "F": f_score, "copilot": copilot_out}, indent=2, ensure_ascii=False))