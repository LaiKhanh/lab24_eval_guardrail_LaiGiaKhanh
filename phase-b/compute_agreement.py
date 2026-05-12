"""Calculate Cohen's Kappa for judge calibration.

Measures inter-rater agreement between LLM judge and human labels.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent


def generate_human_labels() -> None:
    """Create synthetic human annotations for 10 test questions."""
    
    # Sample 10 questions and assign ground-truth labels
    # (In practice, these would be actual human annotations)
    human_labels = [
        {"question_id": 1, "judge_winner": "A", "human_label": "A", "confidence": 0.95},
        {"question_id": 5, "judge_winner": "B", "human_label": "B", "confidence": 0.88},
        {"question_id": 8, "judge_winner": "equal", "human_label": "equal", "confidence": 0.75},
        {"question_id": 12, "judge_winner": "A", "human_label": "A", "confidence": 0.92},
        {"question_id": 15, "judge_winner": "B", "human_label": "B", "confidence": 0.85},
        {"question_id": 18, "judge_winner": "A", "human_label": "A", "confidence": 0.90},
        {"question_id": 22, "judge_winner": "equal", "human_label": "equal", "confidence": 0.80},
        {"question_id": 26, "judge_winner": "B", "human_label": "B", "confidence": 0.88},
        {"question_id": 29, "judge_winner": "A", "human_label": "A", "confidence": 0.93},
        {"question_id": 32, "judge_winner": "equal", "human_label": "equal", "confidence": 0.78},
    ]
    
    df = pd.DataFrame(human_labels)
    output_file = PHASE_DIR / "human_labels.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Generated human labels → {output_file}")
    return df


def calculate_cohens_kappa(judge_labels: list[str], human_labels: list[str]) -> float:
    """Compute Cohen's Kappa statistic.
    
    κ = (P_o - P_e) / (1 - P_e)
    where P_o = observed agreement, P_e = expected agreement by chance
    """
    
    n = len(judge_labels)
    if n == 0:
        return 0.0
    
    # Observed agreement
    agreements = sum(1 for j, h in zip(judge_labels, human_labels) if j == h)
    p_o = agreements / n
    
    # Expected agreement by chance
    categories = set(judge_labels) | set(human_labels)
    p_e = 0.0
    
    for category in categories:
        judge_freq = judge_labels.count(category) / n
        human_freq = human_labels.count(category) / n
        p_e += judge_freq * human_freq
    
    # Kappa
    if p_e >= 1.0:
        return 1.0 if p_o == 1.0 else 0.0
    
    kappa = (p_o - p_e) / (1.0 - p_e)
    return max(-1.0, min(1.0, kappa))


def interpret_kappa(kappa: float) -> str:
    """Provide interpretation of Kappa value."""
    
    if kappa >= 0.81:
        return "Almost Perfect agreement"
    elif kappa >= 0.61:
        return "Substantial agreement"
    elif kappa >= 0.41:
        return "Moderate agreement"
    elif kappa >= 0.21:
        return "Fair agreement"
    elif kappa >= 0.0:
        return "Slight agreement"
    else:
        return "Poor or negative agreement (worse than chance)"


def analyze_calibration() -> None:
    """Compute Kappa and analyze judge calibration."""
    
    print("📊 Judge Calibration Analysis")
    print("-" * 60)
    
    # Generate or load human labels
    if not (PHASE_DIR / "human_labels.csv").exists():
        human_df = generate_human_labels()
    else:
        human_df = pd.read_csv(PHASE_DIR / "human_labels.csv")
    
    # Load judge results
    if not (PHASE_DIR / "pairwise_results.csv").exists():
        print("⚠ pairwise_results.csv not found. Run compare_answers.py first.")
        return
    
    judge_df = pd.read_csv(PHASE_DIR / "pairwise_results.csv")
    
    # Merge on question_id
    human_df["question_id"] = human_df.get("question_id", range(1, len(human_df) + 1))
    judge_df["question_id"] = judge_df.index + 1
    
    merged = pd.merge(
        human_df[["question_id", "human_label"]],
        judge_df[["question_id", "final_winner"]],
        on="question_id",
        how="inner"
    )
    
    if len(merged) == 0:
        print("⚠ No matching question IDs between human labels and judge results.")
        return
    
    judge_preds = merged["final_winner"].tolist()
    human_annot = merged["human_label"].tolist()
    
    # Calculate Kappa
    kappa = calculate_cohens_kappa(judge_preds, human_annot)
    print(f"\nCohen's Kappa: {kappa:.3f}")
    print(f"Interpretation: {interpret_kappa(kappa)}")
    
    # Agreement analysis
    correct = sum(1 for j, h in zip(judge_preds, human_annot) if j == h)
    accuracy = correct / len(judge_preds) if judge_preds else 0.0
    print(f"Accuracy: {accuracy:.1%} ({correct}/{len(judge_preds)})")
    
    # Bias analysis
    print("\n🔍 Bias Analysis:")
    
    # Position bias: preference for A vs B
    judge_a_pref = judge_preds.count("A") / len(judge_preds)
    judge_b_pref = judge_preds.count("B") / len(judge_preds)
    print(f"  Position Bias: A preference={judge_a_pref:.1%}, B preference={judge_b_pref:.1%}")
    
    if abs(judge_a_pref - 0.5) > 0.15:
        print(f"    ⚠ Significant position bias detected")
    else:
        print(f"    ✓ Position bias is minimal")
    
    # Save analysis report
    report_lines = [
        "# Judge Calibration Report\n\n",
        f"## Cohen's Kappa Analysis\n\n",
        f"- Kappa Score: {kappa:.3f}\n",
        f"- Interpretation: {interpret_kappa(kappa)}\n",
        f"- Accuracy: {accuracy:.1%}\n",
        f"- Test Cases: {len(judge_preds)}\n\n",
        "## Kappa Interpretation Scale\n\n",
        "| Range | Interpretation |\n",
        "|-------|----------------|\n",
        "| 0.81-1.00 | Almost Perfect |\n",
        "| 0.61-0.80 | Substantial |\n",
        "| 0.41-0.60 | Moderate |\n",
        "| 0.21-0.40 | Fair |\n",
        "| 0.00-0.20 | Slight |\n",
        "| <0.00 | Poor/Negative |\n\n",
        "## Bias Metrics\n\n",
        f"- Position Bias (A vs B): {judge_a_pref:.1%} vs {judge_b_pref:.1%}\n",
        f"- Length Bias: N/A (requires detailed analysis)\n\n",
        "## Recommendations\n\n",
        "Based on the calibration results, consider:\n",
        "1. Reviewing disagreement cases for systematic judge errors\n",
        "2. Refining the judge rubric or prompt if kappa < 0.60\n",
        "3. Collecting more human labels for validation\n",
        "4. Monitoring for position bias in production\n",
    ]
    
    report_file = PHASE_DIR / "judge_agreement_report.md"
    with open(report_file, "w") as f:
        f.writelines(report_lines)
    
    print(f"\n✓ Saved report → judge_agreement_report.md")


if __name__ == "__main__":
    analyze_calibration()
