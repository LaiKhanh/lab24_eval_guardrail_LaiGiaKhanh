"""Analyze failure patterns and identify improvement opportunities.

Groups bottom-performing questions by root cause and suggests targeted fixes.
"""

from __future__ import annotations

from pathlib import Path
from collections import defaultdict

import pandas as pd


PHASE_DIR = Path(__file__).resolve().parent


def identify_failure_patterns() -> None:
    """Analyze RAGAS results to find systematic failure modes."""
    
    print("🔍 Analyzing Test Set Failures")
    print("-" * 60)
    
    # Load results
    results_df = pd.read_csv(PHASE_DIR / "ragas_results.csv")
    
    # Compute composite score
    results_df["composite_score"] = (
        0.25 * results_df["faithfulness"] +
        0.30 * results_df["answer_relevancy"] +
        0.25 * results_df["context_precision"] +
        0.20 * results_df["context_recall"]
    )
    
    # Sort by composite score
    bottom_10 = results_df.nsmallest(10, "composite_score")
    
    print("📋 Bottom 10 Performing Questions:")
    print()
    
    output_lines = [
        "# Failure Analysis: Bottom Performers\n",
        "## Bottom 10 Questions\n",
        "| Rank | Question | Score | Faithfulness | Relevancy | Precision | Recall |\n",
        "|------|----------|-------|--------------|-----------|-----------|--------|\n",
    ]
    
    for rank, (_, row) in enumerate(bottom_10.iterrows(), 1):
        output_lines.append(
            f"| {rank} | {row['question'][:50]}... | {row['composite_score']:.2f} | "
            f"{row['faithfulness']:.2f} | {row['answer_relevancy']:.2f} | "
            f"{row['context_precision']:.2f} | {row['context_recall']:.2f} |\n"
        )
        print(f"  {rank}. Score={row['composite_score']:.2f}: {row['question'][:60]}...")
    
    output_lines.append("\n## Failure Pattern Analysis\n\n")
    
    # Analyze by weakness type
    print("\n📊 Failure Patterns:")
    
    patterns = defaultdict(list)
    
    for _, row in results_df.iterrows():
        if row["faithfulness"] < 0.70 and row["answer_relevancy"] > 0.75:
            patterns["hallucination"].append(row["question_id"])
        elif row["context_precision"] < 0.65 and row["context_recall"] > 0.75:
            patterns["noisy_retrieval"].append(row["question_id"])
        elif row["context_recall"] < 0.70:
            patterns["incomplete_retrieval"].append(row["question_id"])
        elif row["answer_relevancy"] < 0.65:
            patterns["off_topic_answer"].append(row["question_id"])
    
    # Report patterns
    for pattern_name, question_ids in sorted(patterns.items(), key=lambda x: -len(x[1])):
        print(f"  • {pattern_name.replace('_', ' ').title()}: {len(question_ids)} questions")
        
        output_lines.append(f"### {pattern_name.replace('_', ' ').title()}\n")
        output_lines.append(f"Affected Questions: {len(question_ids)}\n\n")
        
        if pattern_name == "hallucination":
            output_lines.append(
                "**Description:** Model generates facts not supported by retrieved context.\n\n"
                "**Remediation:**\n"
                "1. Enforce response grounding constraint in prompt\n"
                "2. Add verification layer comparing output to context\n"
                "3. Increase temperature safety margins in generation config\n\n"
            )
        elif pattern_name == "noisy_retrieval":
            output_lines.append(
                "**Description:** Retrieved context contains irrelevant documents that don't support the answer.\n\n"
                "**Remediation:**\n"
                "1. Add post-retrieval reranker to filter noisy chunks\n"
                "2. Tune retrieval top-k parameter lower\n"
                "3. Implement metadata filtering to narrow scope\n"
                "4. Consider hybrid search (BM25 + vector) for better precision\n\n"
            )
        elif pattern_name == "incomplete_retrieval":
            output_lines.append(
                "**Description:** Retrieved context is missing necessary evidence to answer the question.\n\n"
                "**Remediation:**\n"
                "1. Increase retrieval top-k to capture more candidates\n"
                "2. Improve chunking strategy to retain context boundaries\n"
                "3. Add query expansion to find semantically similar content\n"
                "4. Review document corpus coverage for question topic\n\n"
            )
        elif pattern_name == "off_topic_answer":
            output_lines.append(
                "**Description:** Generated answer diverges from the user question.\n\n"
                "**Remediation:**\n"
                "1. Add explicit relevance check before generation\n"
                "2. Strengthen question understanding through query rewriting\n"
                "3. Add stop sequences to prevent tangential responses\n\n"
            )
    
    # Summary and recommendations
    output_lines.append("\n## Summary & Recommendations\n\n")
    
    avg_composite = results_df["composite_score"].mean()
    output_lines.append(
        f"- Current average composite score: {avg_composite:.3f}\n"
        f"- {len(results_df)} total questions evaluated\n"
        f"- Bottom {len(bottom_10)} questions account for {bottom_10['composite_score'].sum():.2f} points of failure\n\n"
    )
    
    output_lines.append(
        "**Priority Fixes (by impact):**\n\n"
        "1. **Retrieval Quality** — Highest leverage; fixing retrieval improves multiple metrics\n"
        "2. **Reranking** — Moderate effort, significant precision gain\n"
        "3. **Prompt Engineering** — Low effort, addresses hallucination and relevancy\n"
        "4. **Test Set Refinement** — Identify mislabeled questions that inflate failure counts\n"
    )
    
    # Save analysis
    analysis_file = PHASE_DIR / "analysis_gaps.md"
    with open(analysis_file, "w") as f:
        f.writelines(output_lines)
    
    print(f"\n✓ Saved analysis → analysis_gaps.md")


if __name__ == "__main__":
    identify_failure_patterns()
