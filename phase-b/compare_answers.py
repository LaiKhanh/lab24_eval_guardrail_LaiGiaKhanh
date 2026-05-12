"""Pairwise answer comparison using LLM or fallback judge.

This module implements a robust pairwise judge that mitigates position bias
through swap-and-average methodology.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent
sys.path.insert(0, str(ROOT / "phase-a"))

load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

from rag_adapter import rag_pipeline, load_test_questions


def fetch_openai_judgment(question: str, candidate_a: str, candidate_b: str, order_marker: str) -> str:
    """Get pairwise comparison from OpenAI GPT-4o-mini."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")
    
    prompt = f"""You are comparing two answers to a technical question.

Question: {question}

Answer {order_marker}1: {candidate_a}
Answer {order_marker}2: {candidate_b}

Which answer is better? Rate on:
- Technical accuracy
- Relevance to question
- Clarity and structure
- Completeness

Return JSON only:

{{
  "better": "1|2|equal",
  "confidence": 0.5-1.0,
  "reason": "brief explanation"
}}"""
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("OPENAI_JUDGE_MODEL", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": "You are a precise technical evaluator. Output JSON only."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "max_tokens": 150,
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {e}")


def parse_judgment_response(response_text: str, label_map: dict[str, str]) -> str:
    """Parse LLM or fallback response and extract winner."""
    
    try:
        cleaned = response_text.strip().strip("`").lstrip("json").strip()
        data = json.loads(cleaned)
        winner_raw = str(data.get("better", "equal")).strip()
        if winner_raw in label_map:
            return label_map[winner_raw]
        return "equal"
    except (json.JSONDecodeError, ValueError):
        # Fallback text parsing
        lower = response_text.lower()
        if "better: 1" in lower or '"better": "1"' in lower:
            return label_map.get("1", "equal")
        elif "better: 2" in lower or '"better": "2"' in lower:
            return label_map.get("2", "equal")
        else:
            return "equal"


def local_judge_score(question: str, answer_a: str, answer_b: str) -> str:
    """Deterministic fallback judge when API unavailable."""
    
    q_words = set(w.lower().strip('.,;:!?') for w in question.split())
    a_words = set(w.lower().strip('.,;:!?') for w in answer_a.split())
    b_words = set(w.lower().strip('.,;:!?') for w in answer_b.split())
    
    # Score coverage of question terms
    score_a = len(q_words & a_words) / max(1, len(q_words))
    score_b = len(q_words & b_words) / max(1, len(q_words))
    
    # Length penalty (prefer answers between 15-50 words)
    len_a = len(a_words)
    len_b = len(b_words)
    len_bonus_a = 1.0 if 15 <= len_a <= 50 else 0.8
    len_bonus_b = 1.0 if 15 <= len_b <= 50 else 0.8
    
    final_a = score_a * len_bonus_a
    final_b = score_b * len_bonus_b
    
    if abs(final_a - final_b) < 0.05:
        return "equal"
    elif final_a > final_b:
        return "A"
    else:
        return "B"


def compare_answer_pair(question: str, answer_a: str, answer_b: str, use_llm: bool = False) -> dict:
    """Compare two answers with position bias mitigation.
    
    Runs judgment twice: (A, B) and (B, A). Reconciles disagreements.
    """
    
    results = {"question": question, "answer_a": answer_a, "answer_b": answer_b}
    
    if use_llm:
        try:
            # First run: A then B
            response_1 = fetch_openai_judgment(question, answer_a, answer_b, "")
            winner_1 = parse_judgment_response(response_1, {"1": "A", "2": "B", "equal": "equal"})
            
            # Second run: B then A (swap order)
            response_2 = fetch_openai_judgment(question, answer_b, answer_a, "")
            winner_2 = parse_judgment_response(response_2, {"1": "B", "2": "A", "equal": "equal"})
            
        except Exception as e:
            print(f"  Falling back to local judge: {e}")
            winner_1 = local_judge_score(question, answer_a, answer_b)
            winner_2 = local_judge_score(question, answer_b, answer_a)
    else:
        winner_1 = local_judge_score(question, answer_a, answer_b)
        winner_2 = local_judge_score(question, answer_b, answer_a)
    
    # Reconcile
    if winner_1 == winner_2:
        final_winner = winner_1
    else:
        final_winner = "equal"
    
    results["winner_first_run"] = winner_1
    results["winner_second_run"] = winner_2
    results["final_winner"] = final_winner
    
    return results


def run_pairwise_judgments() -> None:
    """Execute pairwise comparisons on test set."""
    
    print("⚖️  Pairwise Answer Comparison")
    print("-" * 60)
    
    # Load test set
    test_data = pd.read_csv(ROOT / "phase-a" / "testset_v1.csv")
    sample = test_data.head(32)  # Use first 32 questions
    
    use_llm = os.getenv("USE_LLM_JUDGE", "false").strip().lower() in {"1", "true", "yes"}
    print(f"Using LLM Judge: {use_llm}\n")
    
    results = []
    
    for idx, row in tqdm(sample.iterrows(), total=len(sample), desc="Comparing"):
        question = row["question"]
        
        # Generate two candidate answers
        rag_out = rag_pipeline(question)
        base_answer = rag_out["answer"]
        
        # Create variant (different from original implementation)
        variant_answer = base_answer.split('.')[0] + '. ' + base_answer.split('.')[-1] if '.' in base_answer else base_answer + " (verified)"
        
        # Compare
        comparison = compare_answer_pair(question, base_answer, variant_answer, use_llm=use_llm)
        results.append(comparison)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_file = PHASE_DIR / "pairwise_results.csv"
    results_df.to_csv(results_file, index=False)
    
    print(f"\n✓ Saved pairwise results → {results_file}")
    print(f"  Total comparisons: {len(results_df)}")
    print(f"  Agreement rate: {(results_df['winner_first_run'] == results_df['winner_second_run']).sum() / len(results_df) * 100:.1f}%")


if __name__ == "__main__":
    run_pairwise_judgments()
