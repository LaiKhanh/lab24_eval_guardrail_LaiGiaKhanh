"""Multi-profile judge aggregation for robust evaluation.

Combines multiple judge profiles (accuracy-first, conciseness-first, completeness-first)
with optional LLM judge to reduce individual bias.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import numpy as np


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent


class JudgeProfile:
    """Base class for different judge profiles."""
    
    def __init__(self, name: str):
        self.name = name
    
    def score_answer(self, question: str, answer: str) -> float:
        """Return a score from 0 to 100."""
        raise NotImplementedError


class AccuracyFirstJudge(JudgeProfile):
    """Prioritizes factual accuracy and domain knowledge."""
    
    def __init__(self):
        super().__init__("Accuracy-First Judge")
        self.keywords = {
            "metric", "framework", "algorithm", "data", "technical",
            "implementation", "process", "system", "architecture"
        }
    
    def score_answer(self, question: str, answer: str) -> float:
        q_terms = set(w.lower() for w in question.split())
        a_terms = set(w.lower() for w in answer.split())
        
        # Match rate
        match_rate = len(q_terms & a_terms) / max(1, len(q_terms))
        
        # Check for strong technical terms
        tech_term_count = sum(1 for w in a_terms if w in self.keywords)
        tech_score = min(1.0, tech_term_count / 3.0)
        
        combined = 0.6 * match_rate + 0.4 * tech_score
        return int(combined * 100)


class ConcisenessFirstJudge(JudgeProfile):
    """Prioritizes brevity and directness."""
    
    def score_answer(self, question: str, answer: str) -> float:
        q_terms = set(w.lower() for w in question.split())
        a_terms = set(w.lower() for w in answer.split())
        
        # Match rate
        match_rate = len(q_terms & a_terms) / max(1, len(q_terms))
        
        # Word count penalty (prefer 15-35 words)
        word_count = len(a_terms)
        if 15 <= word_count <= 35:
            length_score = 1.0
        elif 10 <= word_count <= 50:
            length_score = 0.85
        else:
            length_score = 0.6
        
        combined = 0.7 * match_rate + 0.3 * length_score
        return int(combined * 100)


class CompletenessFirstJudge(JudgeProfile):
    """Prioritizes comprehensive coverage."""
    
    def score_answer(self, question: str, answer: str) -> float:
        q_terms = set(w.lower() for w in question.split())
        a_terms = set(w.lower() for w in answer.split())
        
        # Match rate
        match_rate = len(q_terms & a_terms) / max(1, len(q_terms))
        
        # Length bonus (more comprehensive)
        word_count = len(a_terms)
        length_score = min(1.0, word_count / 50.0)
        
        combined = 0.6 * match_rate + 0.4 * length_score
        return int(combined * 100)


def score_all_answers() -> None:
    """Score test set answers using multiple profiles."""
    
    print("🏆 Multi-Profile Judge Scoring")
    print("-" * 60)
    
    # Load test set
    test_df = pd.read_csv(ROOT / "phase-a" / "testset_v1.csv")
    
    # Initialize judges
    judges = [
        AccuracyFirstJudge(),
        ConcisenessFirstJudge(),
        CompletenessFirstJudge(),
    ]
    
    results = []
    
    for idx, row in test_df.iterrows():
        question = row["question"]
        ground_truth = row["ground_truth"]
        
        # Score with each profile
        scores = {}
        for judge in judges:
            score = judge.score_answer(question, ground_truth)
            scores[judge.name] = score
        
        # Aggregate (simple average)
        average_score = int(np.mean(list(scores.values())))
        
        # Winner (majority)
        winners = [j.name for j in judges]
        
        results.append({
            "question_id": idx + 1,
            "question": question,
            "accuracy_judge_score": scores[judges[0].name],
            "conciseness_judge_score": scores[judges[1].name],
            "completeness_judge_score": scores[judges[2].name],
            "average_score": average_score,
            "primary_winner": judges[np.argmax([scores[j.name] for j in judges])].name,
        })
    
    # Save scores
    results_df = pd.DataFrame(results)
    output_file = PHASE_DIR / "absolute_scores.csv"
    results_df.to_csv(output_file, index=False)
    
    print(f"✓ Scored {len(results_df)} answers with 3 judge profiles")
    print(f"✓ Saved scores → {output_file}")
    print(f"\nAverage Scores by Profile:")
    print(f"  Accuracy-First:      {results_df['accuracy_judge_score'].mean():.1f}/100")
    print(f"  Conciseness-First:   {results_df['conciseness_judge_score'].mean():.1f}/100")
    print(f"  Completeness-First:  {results_df['completeness_judge_score'].mean():.1f}/100")
    print(f"  Aggregated Average:  {results_df['average_score'].mean():.1f}/100")


if __name__ == "__main__":
    score_all_answers()
