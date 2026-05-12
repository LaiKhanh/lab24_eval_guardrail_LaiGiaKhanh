"""Generate a diverse, high-quality test set for evaluation.

This module uses a different curation strategy than the original: focuses on
orthogonal failure modes and includes practical edge cases.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Literal

import pandas as pd


PHASE_DIR = Path(__file__).resolve().parent


def create_test_questions() -> list[dict]:
    """Generate 50 test questions covering Lab 24 scope.
    
    Distribution:
    - 25 foundational questions (simple, one-step reasoning)
    - 12 multi-step reasoning questions
    - 13 multi-document synthesis questions
    """
    
    foundational = [
        {
            "q": "What is the primary purpose of RAG evaluation?",
            "t": "RAG evaluation measures whether a system can retrieve relevant context and generate answers grounded in that context.",
            "type": "simple",
        },
        {
            "q": "Define faithfulness in the context of RAG metrics.",
            "t": "Faithfulness measures whether an answer is supported by and grounded in the retrieved context, avoiding hallucinations.",
            "type": "simple",
        },
        {
            "q": "What does answer relevancy measure in RAGAS?",
            "t": "Answer relevancy quantifies whether the generated answer directly addresses the user's question without tangents.",
            "type": "simple",
        },
        {
            "q": "Explain context precision in retrieval evaluation.",
            "t": "Context precision measures the fraction of retrieved documents that are actually relevant to the question.",
            "type": "simple",
        },
        {
            "q": "What is context recall?",
            "t": "Context recall measures whether all necessary evidence needed to answer the question was retrieved.",
            "type": "simple",
        },
        {
            "q": "What are input guardrails?",
            "t": "Input guardrails validate user queries for scope compliance, detect PII, and block prompt injection attacks.",
            "type": "simple",
        },
        {
            "q": "What types of PII should be detected?",
            "t": "PII types include email addresses, phone numbers, national IDs, bank accounts, names, and other personal identifiers.",
            "type": "simple",
        },
        {
            "q": "What is prompt injection?",
            "t": "Prompt injection attempts to manipulate the model by inserting hidden instructions or bypassing safety constraints.",
            "type": "simple",
        },
        {
            "q": "What are output guardrails?",
            "t": "Output guardrails filter final responses to prevent harmful content, private data leaks, and policy violations.",
            "type": "simple",
        },
        {
            "q": "What is an LLM-as-judge?",
            "t": "LLM-as-judge uses a language model to compare or score answers, calibrated against human annotations.",
            "type": "simple",
        },
        {
            "q": "What is pairwise comparison in evaluation?",
            "t": "Pairwise comparison judges two candidate answers for the same question and selects the better one.",
            "type": "simple",
        },
        {
            "q": "What is position bias in LLM judging?",
            "t": "Position bias is the tendency for judges to favor the first presented option regardless of quality.",
            "type": "simple",
        },
        {
            "q": "What is Cohen's Kappa?",
            "t": "Cohen's Kappa measures inter-rater agreement between human labels and judge predictions, accounting for chance.",
            "type": "simple",
        },
        {
            "q": "What is latency P95?",
            "t": "P95 latency is the 95th percentile response time, meaning 95% of requests complete within this duration.",
            "type": "simple",
        },
        {
            "q": "What are SLOs?",
            "t": "SLOs (Service Level Objectives) define target availability, latency, and accuracy metrics for production systems.",
            "type": "simple",
        },
        {
            "q": "What is an incident playbook?",
            "t": "An incident playbook documents how to detect, diagnose, and resolve specific failure scenarios.",
            "type": "simple",
        },
        {
            "q": "What is a CI/CD evaluation gate?",
            "t": "A CI/CD gate automatically runs evaluation on code changes and blocks merges if metrics fall below thresholds.",
            "type": "simple",
        },
        {
            "q": "What is text chunking in RAG?",
            "t": "Chunking divides long documents into overlapping segments that can be indexed and retrieved independently.",
            "type": "simple",
        },
        {
            "q": "What is hybrid search?",
            "t": "Hybrid search combines keyword-based (BM25) and semantic (vector) retrieval to balance recall and precision.",
            "type": "simple",
        },
        {
            "q": "What is reranking in RAG?",
            "t": "Reranking uses a specialized model to re-order initial retrieval results by relevance before passing to generation.",
            "type": "simple",
        },
        {
            "q": "What is metadata filtering?",
            "t": "Metadata filtering restricts retrieval to documents with specific attributes (date, source, category) before vector search.",
            "type": "simple",
        },
        {
            "q": "What is false positive rate in safety filtering?",
            "t": "False positive rate measures the fraction of safe content incorrectly flagged as unsafe by the guard.",
            "type": "simple",
        },
        {
            "q": "What is precision in adversarial testing?",
            "t": "Precision in security testing measures the fraction of detected attacks that were actually attack attempts.",
            "type": "simple",
        },
        {
            "q": "What are common adversarial attack types?",
            "t": "Common attacks include jailbreaks, prompt injection, role-playing exploits, encoding-based bypasses, and semantic confusion.",
            "type": "simple",
        },
        {
            "q": "What is throughput in performance benchmarking?",
            "t": "Throughput measures the number of successful requests processed per unit time (e.g., requests per second).",
            "type": "simple",
        },
        {
            "q": "What is cost per query in operations?",
            "t": "Cost per query includes API charges, infrastructure overhead, and operational costs amortized across request volume.",
            "type": "simple",
        },
    ]
    
    reasoning = [
        {
            "q": "How would you detect if a RAG system is hallucinating rather than retrieving?",
            "t": "Compare faithfulness scores across retrieval methods: high scores with retrieval + low without retrieval indicates genuine retrieval value.",
            "type": "reasoning",
        },
        {
            "q": "Why is context precision important even when context recall is perfect?",
            "t": "Low precision adds noise that confuses the model and increases latency, so optimizing precision reduces downstream problems.",
            "type": "reasoning",
        },
        {
            "q": "How can position bias compromise judge calibration?",
            "t": "If judges systematically prefer first answers, then observed judge accuracy may be artificially high and not generalize.",
            "type": "reasoning",
        },
        {
            "q": "What is the relationship between false positive rate and user trust in guardrails?",
            "t": "High false positives block legitimate queries and frustrate users; low false positives increase user trust and adoption.",
            "type": "reasoning",
        },
        {
            "q": "Why should latency be measured per pipeline layer rather than only end-to-end?",
            "t": "Per-layer measurement identifies bottlenecks (e.g., retrieval vs. generation) so engineers can optimize high-impact components.",
            "type": "reasoning",
        },
        {
            "q": "How would you prioritize guardrail improvements if PII recall is 75% and adversarial detection is 60%?",
            "t": "Prioritize adversarial detection because it has lower baseline performance and higher impact on system trustworthiness.",
            "type": "reasoning",
        },
        {
            "q": "What metric gap would indicate that chunking strategy is suboptimal?",
            "t": "If context recall is significantly lower than context precision, chunking is likely losing relevant evidence.",
            "type": "reasoning",
        },
        {
            "q": "How does test set diversity affect the reliability of evaluation results?",
            "t": "Diverse test sets across question types and domains reveal failure patterns; homogeneous sets may hide systematic issues.",
            "type": "reasoning",
        },
        {
            "q": "Why run adversarial tests if the system is already passing functional tests?",
            "t": "Functional tests measure normal cases; adversarial tests reveal vulnerability to sophisticated attacks from motivated actors.",
            "type": "reasoning",
        },
        {
            "q": "What problem could arise if SLO targets are set without analyzing cost implications?",
            "t": "Overly aggressive SLOs (e.g., P99 < 10ms) may require expensive infrastructure, making the system economically unviable.",
            "type": "reasoning",
        },
        {
            "q": "How would you validate that a CI/CD evaluation gate is preventing quality regression?",
            "t": "Compare production quality metrics before and after enabling the gate; a well-tuned gate should show improvement.",
            "type": "reasoning",
        },
        {
            "q": "Why is it insufficient to only measure average latency without percentiles?",
            "t": "Average latency can hide long-tail outliers; P95/P99 captures user experience for slower-than-average requests.",
            "type": "reasoning",
        },
        {
            "q": "What would explain a situation where Cohen's Kappa is low but absolute scores are high?",
            "t": "Judges may agree on overall quality but disagree on which answers are better pairwise (different ranking preference).",
            "type": "reasoning",
        },
    ]
    
    synthesis = [
        {
            "q": "Design a guardrail stack that balances security, user experience, and operational complexity for a support chatbot.",
            "t": "Use scope validation, PII detection, and adversarial filtering at input; add output safety and rate limiting. Prioritize reducing false positives for UX.",
            "type": "multi_context",
        },
        {
            "q": "How would you debug a situation where faithfulness is high but answer relevancy is low?",
            "t": "Model generates text that is grounded in context but answers the wrong question. Check question understanding and answer synthesis logic.",
            "type": "multi_context",
        },
        {
            "q": "Propose a calibration strategy if your LLM judge disagrees with humans on 40% of test cases.",
            "t": "Analyze disagreement patterns, adjust judge prompts or rubric, collect more human labels in disagreement areas, and retrain if using supervised methods.",
            "type": "multi_context",
        },
        {
            "q": "How would you design a cost-effective latency benchmarking system for continuous monitoring?",
            "t": "Sample requests in production (1-5%), capture latency by layer, store in time-series DB, compute P50/P95/P99 hourly, alert on SLO violations.",
            "type": "multi_context",
        },
        {
            "q": "What metrics would you track to detect whether your adversarial defense is improving over time?",
            "t": "Track detection rate, false positive rate, new attack types encountered, and time-to-fix for newly discovered vulnerabilities.",
            "type": "multi_context",
        },
        {
            "q": "How would you test the robustness of PII detection when model performance varies across PII types?",
            "t": "Create domain-specific test sets (emails, phone, IDs, names), measure recall per type, identify weak areas, and apply targeted improvements.",
            "type": "multi_context",
        },
        {
            "q": "Design a human-in-the-loop evaluation process that maintains high quality while scaling beyond 100 test questions.",
            "t": "Use judge for initial filtering, have humans review lowest-confidence predictions and disagreements, update judge thresholds based on feedback.",
            "type": "multi_context",
        },
        {
            "q": "How would you structure an SLO that incorporates both individual metrics (faithfulness, latency) and user-facing outcomes?",
            "t": "Create component SLOs for retrieval, generation, guardrails; aggregate to system SLOs; map to user-facing outcomes like 'satisfactory answer rate'.",
            "type": "multi_context",
        },
        {
            "q": "What would be your incident response priority if both latency spike and adversarial attack detection rate drop simultaneously?",
            "t": "Prioritize latency because slower system may indicate attack or load; investigation might reveal if attack is causing slowdown.",
            "type": "multi_context",
        },
        {
            "q": "How would you design test set generation to ensure it covers both common use cases and rare edge cases?",
            "t": "Use stratified sampling from production queries plus targeted generation for edge cases (ambiguous questions, multilingual, extreme length).",
            "type": "multi_context",
        },
        {
            "q": "Propose a strategy to identify whether test set labeling errors are affecting evaluation metrics.",
            "t": "Have multiple annotators label random subset, compute inter-annotator agreement, audit low-agreement questions, correct if errors found.",
            "type": "multi_context",
        },
        {
            "q": "How would you configure a CI/CD gate to prevent both false positives (blocking good PRs) and false negatives (allowing regressions)?",
            "t": "Set thresholds conservatively, monitor gate false positive rate, require optional fallback review, and adjust thresholds based on observed false rates.",
            "type": "multi_context",
        },
        {
            "q": "Design a guardrail testing strategy that covers both known attacks and unknown unknowns.",
            "t": "Use known attack patterns, red-team with security experts, monitor production for new patterns, and run continuous fuzzing.",
            "type": "multi_context",
        },
    ]
    
    all_questions = foundational + reasoning + synthesis
    return all_questions


def save_test_set(questions: list[dict]) -> None:
    """Convert questions to CSV and save to testset_v1.csv."""
    
    rows = []
    for question in questions:
        rows.append({
            "question": question["q"],
            "ground_truth": question["t"],
            "contexts": "generic",  # Placeholder; filled by RAG adapter
            "evolution_type": question["type"],
        })
    
    df = pd.DataFrame(rows)
    output_file = PHASE_DIR / "testset_v1.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Generated {len(rows)} test questions → {output_file}")
    print(f"  Distribution: {sum(1 for q in questions if q['type']=='simple')} simple, "
          f"{sum(1 for q in questions if q['type']=='reasoning')} reasoning, "
          f"{sum(1 for q in questions if q['type']=='multi_context')} multi-context")


if __name__ == "__main__":
    questions = create_test_questions()
    save_test_set(questions)
