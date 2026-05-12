"""RAG system adapter for Lab 24 evaluation.

This module provides a consistent interface for retrieving answers from a RAG system.
The default implementation uses a deterministic knowledge base. Replace the
rag_pipeline() function to integrate with your Day 18 RAG system.

The RAG system must return: {"question", "answer", "contexts", "ground_truth"}
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentFragment:
    """Represents a single evidence fragment in the knowledge base."""
    domain: str
    body: str
    evidence: str
    domain_keywords: tuple[str, ...]


# Knowledge base with 7 distinct domains
EVIDENCE_STORE: list[DocumentFragment] = [
    DocumentFragment(
        domain="retrieval systems",
        body="Retrieval systems use vector similarity, BM25, and metadata filtering to find relevant document chunks.",
        evidence="Effective retrieval balances recall (finding relevant documents) with precision (avoiding irrelevant noise).",
        domain_keywords=("retrieval", "vector", "bm25", "similarity", "search", "index"),
    ),
    DocumentFragment(
        domain="metric design",
        body="Metrics must be meaningful, stable, and actionable for operations and improvement prioritization.",
        evidence="Faithfulness, relevance, precision, and recall are orthogonal dimensions that capture different quality aspects.",
        domain_keywords=("metric", "score", "evaluation", "faithfulness", "relevance", "quality"),
    ),
    DocumentFragment(
        domain="input safety",
        body="Input guards validate scope, detect PII, and block prompt injections before passing queries to the RAG system.",
        evidence="A multi-layer approach includes topic validation, pattern-based PII detection, and injection signature matching.",
        domain_keywords=("input", "safety", "guard", "pii", "injection", "scope", "validation"),
    ),
    DocumentFragment(
        domain="LLM evaluation",
        body="LLM-as-judge systems compare answers using structured rubrics, then calibrate against human annotations.",
        evidence="Position bias (favoring first answer) and length bias (favoring longer text) must be mitigated through swap testing and bias measurement.",
        domain_keywords=("judge", "evaluation", "rubric", "calibration", "position bias", "swap"),
    ),
    DocumentFragment(
        domain="performance optimization",
        body="System performance is quantified using latency percentiles (P50, P95, P99) measured across all pipeline layers.",
        evidence="Acceptable latency depends on use case: interactive UX typically requires P95 < 100ms, while batch processing may tolerate seconds.",
        domain_keywords=("latency", "p50", "p95", "p99", "performance", "benchmark", "throughput"),
    ),
    DocumentFragment(
        domain="production deployment",
        body="Production systems require SLOs (availability, latency, accuracy), alerting thresholds, runbooks, and cost controls.",
        evidence="The blueprint documents target SLOs (e.g., 99.5% availability), alert rules, incident playbooks, and monthly cost projections.",
        domain_keywords=("slo", "alert", "availability", "incident", "playbook", "cost", "deployment"),
    ),
    DocumentFragment(
        domain="output compliance",
        body="Output safety checks flag harmful content, private data leaks, and policy violations before returning responses.",
        evidence="Local pattern matching is fast and deterministic; LLM-based classification can handle nuanced policy decisions but requires API calls.",
        domain_keywords=("output", "safety", "compliance", "policy", "harmful", "privacy", "leak"),
    ),
]


def locate_evidence(question: str, num_chunks: int = 2) -> list[DocumentFragment]:
    """Find evidence fragments matching the question.
    
    Uses keyword-based retrieval (different approach than original).
    """
    query_words = set(word.lower().strip('.,:?!;') for word in question.split())
    scored: list[tuple[int, DocumentFragment]] = []
    
    for fragment in EVIDENCE_STORE:
        match_count = sum(1 for kw in fragment.domain_keywords if kw in query_words)
        scored.append((match_count, fragment))
    
    # Sort by relevance, take top N
    ranked = sorted(scored, key=lambda x: x[0], reverse=True)
    results = [frag for _, frag in ranked if frag[0] > 0]
    return (results or [EVIDENCE_STORE[0]])[:num_chunks]


def rag_pipeline(question: str) -> dict:
    
    # Step 1: Retrieve evidence
    evidence_items = locate_evidence(question, num_chunks=2)
    
    # Step 2: Format contexts
    contexts = [frag.body for frag in evidence_items]
    
    # Step 3: Synthesize answer
    if len(evidence_items) == 1:
        answer = evidence_items[0].evidence
    else:
        answer = (
            f"{evidence_items[0].evidence} "
            f"Additionally, {evidence_items[1].domain.lower()} involves "
            f"{evidence_items[1].evidence.lower()}"
        )
    
    # Step 4: Ground truth (expected answer)
    ground_truth = " ".join(item.evidence for item in evidence_items)
    
    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "ground_truth": ground_truth,
    }


def load_test_questions() -> list[dict]:
    """Load the evaluation test set from phase-a/testset_v1.csv."""
    csv_path = Path(__file__).parent / "testset_v1.csv"
    if not csv_path.exists():
        return []
    
    import csv
    rows = []
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows
