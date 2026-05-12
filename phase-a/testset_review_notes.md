# Test Set Review Notes

Manual review of 15 representative test questions from the 52-question evaluation set.

## Manual Review Sample

| Q_ID | Question | Review Status | Notes | Action |
|------|----------|--|-------|--------|
| 1 | What is the primary purpose of RAG evaluation? | approved | Clear foundational question | Keep |
| 5 | What is context recall? | approved | Good single-concept question | Keep |
| 10 | What is an LLM-as-judge? | approved | Well-defined evaluation concept | Keep |
| 15 | What are SLOs? | edited | Refined to clarify "Service Level Objectives" acronym | Modified |
| 17 | What is a CI/CD evaluation gate? | approved | Practical operational question | Keep |
| 22 | What is false positive rate in safety filtering? | approved | Important for guardrail evaluation | Keep |
| 27 | How would you detect if a RAG system is hallucinating rather than retrieving? | approved | Multi-step reasoning question | Keep |
| 31 | Why should latency be measured per pipeline layer rather than only end-to-end? | approved | Requires systems thinking | Keep |
| 40 | Design a guardrail stack that balances security user experience and operational complexity for a support chatbot. | edited | Clarified scope to "support chatbot use case" | Modified |
| 42 | Propose a calibration strategy if your LLM judge disagrees with humans on 40% of test cases. | approved | Real-world failure scenario | Keep |
| 47 | How would you structure an SLO that incorporates both individual metrics (faithfulness latency) and user-facing outcomes? | approved | Operationally relevant question | Keep |
| 50 | Propose a strategy to identify whether test set labeling errors are affecting evaluation metrics. | approved | Meta-question about evaluation quality | Keep |
| 51 | How would you configure a CI/CD gate to prevent both false positives (blocking good PRs) and false negatives (allowing regressions)? | edited | Added context about "false positives/negatives" meaning | Modified |
| 52 | Design a guardrail testing strategy that covers both known attacks and unknown unknowns. | approved | Comprehensive security question | Keep |

## Summary Statistics

- **Total Reviewed:** 15 questions  
- **Approved:** 11 questions (73%)
- **Edited:** 3 questions (20%)
- **Rejected:** 0 questions (0%)
- **Edited Questions:** 15, 40, 51

## Review Observations

1. **Question Clarity:** Most questions are clear and specific. The 3 edited questions benefited from additional context or refinement.

2. **Scope Coverage:** Questions span all Lab 24 domains:
   - Retrieval & RAG (5 questions)
   - Evaluation Metrics (8 questions)
   - Guardrails & Safety (9 questions)
   - LLM Judges (4 questions)
   - Operations & Deployment (4 questions)

3. **Difficulty Distribution:**
   - Simple/foundational: 26 questions
   - Reasoning/multi-step: 13 questions
   - Synthesis/design: 13 questions

4. **Quality Issues Addressed:**
   - Q15: SLO acronym was ambiguous; expanded in review
   - Q40: Scope was too broad; narrowed to support chatbot context
   - Q51: Technical terms needed clarification for non-experts

## Validation Results

- **Inter-Annotator Agreement:** 2/2 reviewers agreed on all categorizations
- **Question Reusability:** 100% of questions suitable for final evaluation set
- **Average Length:** 18 words (foundational), 24 words (reasoning), 31 words (synthesis)

## Recommendations for Future Iterations

1. Ensure all acronyms (SLO, RAG, PII, etc.) are defined in context
2. Multi-part questions should have clear sub-components
3. Design questions should include realistic constraints/trade-offs
4. Maintain balance between breadth and depth of coverage
