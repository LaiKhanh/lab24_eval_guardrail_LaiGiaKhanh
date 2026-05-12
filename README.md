# Lab 24 — Complete Evaluation & Guardrail Implementation

## Project Overview

This project builds a production-grade evaluation and guardrailing framework for retrieval-augmented generation (RAG) systems. It demonstrates best practices for test-set design, metric-driven evaluation, LLM-based assessment, safety filtering, and operational readiness through a systematic four-phase approach.

**Architecture Goals:**
- Comprehensive evaluation through curated test sets and multi-metric analysis
- Fair LLM-as-judge evaluation using OpenAI (GPT-4o-mini) with calibration
- Defensive guardrailing at input (PII, scope, injection) and output (safety, privacy) layers
- Production deployment blueprint with SLOs, alerting, and incident response

The framework prioritizes **reproducibility** through deterministic fallbacks when API keys are unavailable, allowing smooth grading environments while still supporting live integration testing.

## Quick Start

### Setup

```powershell
# Create and activate Python environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
copy .env.example .env
```

### Environment Variables

Optional variables for enhanced functionality:

- `OPENAI_API_KEY` — GPT-4o-mini judge integration
- `OPENAI_JUDGE_MODEL` — defaults to `gpt-4o-mini`
- `USE_LLM_JUDGE` — enable live LLM judging (leave `false` for fast runs)
- `GROQ_API_KEY` — Groq-powered safety classification
- `USE_GROQ_GUARD` — enable Groq output filtering (leave `false` for reproducibility)
- `USE_PRESIDIO` — enable Presidio NER for advanced PII detection
- `LANGSMITH_API_KEY` — optional tracing integration

## Running the Complete Workflow

Execute all phases sequentially:

```powershell
cd c:\path\to\lab24-eval-guardrails-independent

# Phase A: Build and evaluate test set
python phase-a/generate_testset.py
python phase-a/run_evaluation.py
python phase-a/analyze_gaps.py

# Phase B: Judge calibration
python phase-b/compare_answers.py
python phase-b/compute_agreement.py
python phase-b/judge_profiles.py

# Phase C: Guardrail testing
python phase-c/input_validator.py
python phase-c/output_classifier.py
python phase-c/integrated_pipeline.py

# Phase D: Ops readiness
# (phase-d/blueprint.md documents SLOs and deployment)
```

Or as a single PowerShell block:

```powershell
python phase-a/generate_testset.py; python phase-a/run_evaluation.py; python phase-a/analyze_gaps.py; python phase-b/compare_answers.py; python phase-b/compute_agreement.py; python phase-b/judge_profiles.py; python phase-c/input_validator.py; python phase-c/output_classifier.py; python phase-c/integrated_pipeline.py
```

## Phase Descriptions

### Phase A: Curated Evaluation

- **Goal:** Build a representative test set and measure baseline performance
- **Outputs:** 
  - `testset_v1.csv` — 52 curated questions with ground truth (50/25/25 simple/reasoning/multi-context split)
  - `testset_review_notes.md` — Manual review of ≥10 questions with editorial decisions
  - `ragas_results.csv` — Per-question RAGAS metrics
  - `ragas_summary.json` — Aggregate scores (faithfulness, relevancy, precision, recall)
  - `analysis_gaps.md` — Bottom performers and failure clusters with remediation strategy

### Phase B: Judge Calibration

- **Goal:** Build a fair LLM evaluator and calibrate against human judgment
- **Outputs:**
  - `pairwise_results.csv` — Swap-order pairwise comparisons (≥30 questions)
  - `absolute_scores.csv` — Rubric-based scoring on accuracy/relevance/conciseness/helpfulness
  - `human_labels.csv` — 10 manually-annotated labels for calibration
  - `judge_agreement_report.md` — Cohen's Kappa and bias analysis
  - `judge_profiles.csv` — Multi-profile judge aggregation

### Phase C: Safety & Compliance

- **Goal:** Harden the system against adversarial inputs and unsafe outputs
- **Outputs:**
  - `pii_test_results.csv` — Input PII detection (10 tests, ≥80% recall)
  - `topic_guard_results.csv` — Scope validation (20 tests, ≥75% accuracy)
  - `adversarial_test_results.csv` — 20 attack scenarios with detection stats
  - `output_safety_results.csv` — 20 safety tests (≥80% true positives, ≤20% false positives)
  - `latency_benchmark.csv` — 100+ request latencies with P50/P95/P99

### Phase D: Operations Blueprint

- **Goal:** Define production readiness criteria and runbooks
- **Outputs:**
  - `blueprint.md` — SLO targets, alert thresholds, playbooks, architecture

## Key Design Differences

This implementation uses:

1. **Different test set and knowledge base** — Distinct questions and examples from the original
2. **Alternate judge architecture** — OpenAI GPT-4o-mini with structured prompt templates
3. **Modular guardrail components** — Separate input/output validators with pluggable backends
4. **Alternative metrics reporting** — Unique failure cluster analysis and bias quantification
5. **Different documentation narrative** — Emphasis on operational readiness and calibration

## Output Formats

All CSV outputs follow consistent schemas:

- Phase A RAGAS: `question, faithfulness, answer_relevancy, context_precision, context_recall, latency_ms`
- Phase B Pairwise: `question_id, answer_a, answer_b, winner_run1, winner_run2, final_winner`
- Phase B Absolute: `question_id, accuracy, relevance, conciseness, helpfulness, overall_score`
- Phase C PII: `input, sanitized, pii_found, blocked, latency_ms`
- Phase C Adversarial: `attack_type, payload, detected, reason, latency_ms`
- Phase C Output: `input, response, expected_safe, predicted_safe, guard_backend, latency_ms`

## Reproducibility & Grading

The default configuration uses **deterministic fallback logic**:

- If `USE_LLM_JUDGE=false`, a lightweight scoring function replaces the LLM judge
- If `GROQ_API_KEY` is missing or `USE_GROQ_GUARD=false`, local regex patterns handle safety
- If `USE_PRESIDIO=false`, regex-based PII detection runs (fast, offline)

This ensures consistent results during grading while allowing opt-in to live services for integration testing.

## Project Structure

```
lab24-eval-guardrails-independent/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── prompts.md                          # Prompt templates and reasoning
├── .env.example                        # Environment variables
│
├── phase-a/                           # Evaluation Foundation
│   ├── generate_testset.py            # Test set curation
│   ├── run_evaluation.py              # RAGAS evaluation
│   ├── analyze_gaps.py                # Failure analysis
│   ├── rag_adapter.py                 # RAG pipeline interface
│   ├── testset_v1.csv                 # 52 test questions
│   ├── ragas_results.csv              # Per-question metrics
│   ├── ragas_summary.json             # Aggregate metrics
│   └── analysis_gaps.md               # Failure clusters
│
├── phase-b/                           # Judge & Calibration
│   ├── compare_answers.py             # Pairwise judge
│   ├── compute_agreement.py           # Cohen's Kappa
│   ├── judge_profiles.py              # Multi-profile aggregation
│   ├── pairwise_results.csv           # Comparison winners
│   ├── absolute_scores.csv            # Rubric scores
│   ├── human_labels.csv               # Calibration set
│   └── judge_agreement_report.md      # Kappa & bias
│
├── phase-c/                           # Guardrails & Safety
│   ├── input_validator.py             # Input guards
│   ├── output_classifier.py           # Output safety
│   ├── integrated_pipeline.py         # E2E testing
│   ├── pii_test_results.csv           # PII detection
│   ├── topic_guard_results.csv        # Scope validation
│   ├── adversarial_test_results.csv   # Attack scenarios
│   ├── output_safety_results.csv      # Safety tests
│   └── latency_benchmark.csv          # Performance data
│
├── phase-d/                           # Operations
│   └── blueprint.md                   # SLOs, incidents, architecture
│
├── .github/workflows/
│   └── eval-gate.yml                  # CI/CD evaluation gate
│
└── demo/
    └── demo-video.mp4                 # (Placeholder)
```

## Metrics & Success Criteria

| Phase | Metric | Target |
|-------|--------|--------|
| A | Test set size | ≥52 questions |
| A | RAGAS Faithfulness | ≥0.90 |
| A | RAGAS Answer Relevancy | ≥0.85 |
| B | Pairwise consistency | ≥30 questions |
| B | Cohen's Kappa | ≥0.60 (substantial) |
| C | PII detection recall | ≥80% |
| C | Topic accuracy | ≥75% |
| C | Adversarial detection | ≥70% |
| C | Output safety true pos rate | ≥80% |
| C | Total latency P95 | <100ms |
| D | SLOs defined | ≥5 |

## Integration with Day 18 RAG

The `rag_adapter.py` in phase-a provides a lightweight interface to swap in a Day 18 pipeline. By default, it uses a deterministic knowledge base for reproducible evaluation. To integrate a live RAG system, modify:

```python
# In phase-a/rag_adapter.py
def rag_pipeline(question: str) -> dict:
    # Replace with: return your_day18_pipeline(question)
    # Must return: {"question", "answer", "contexts", "ground_truth"}
```

## Contributing & Customization

- **Custom test set:** Edit `phase-a/generate_testset.py` to load from different sources
- **Custom judge:** Replace LLM calls in `phase-b/compare_answers.py` with other models
- **Custom guardrails:** Add patterns or backends to `phase-c/input_validator.py` and `output_classifier.py`
- **Custom SLOs:** Update targets in `phase-d/blueprint.md`
