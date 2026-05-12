# Failure Analysis: Bottom Performers

## Bottom 10 Questions

| Rank | Question | Score | Faithfulness | Relevancy | Precision | Recall |
|------|----------|-------|--------------|-----------|-----------|--------|
| 1 | Design a guardrail stack that... | 0.885 | 0.905 | 0.878 | 0.712 | 0.845 |
| 2 | How would you debug a situation... | 0.898 | 0.911 | 0.889 | 0.734 | 0.868 |
| 3 | Propose a calibration strategy... | 0.901 | 0.918 | 0.903 | 0.751 | 0.883 |
| 4 | How would you design a cost... | 0.903 | 0.914 | 0.896 | 0.742 | 0.872 |
| 5 | What metrics would you track... | 0.908 | 0.920 | 0.908 | 0.765 | 0.892 |
| 6 | How would you test the robustness... | 0.911 | 0.917 | 0.901 | 0.756 | 0.878 |
| 7 | Design a human-in-the-loop... | 0.912 | 0.912 | 0.892 | 0.739 | 0.870 |
| 8 | How would you structure an SLO... | 0.914 | 0.915 | 0.898 | 0.748 | 0.878 |
| 9 | What would be your incident... | 0.917 | 0.919 | 0.905 | 0.762 | 0.887 |
| 10 | How would you design test set... | 0.918 | 0.916 | 0.899 | 0.753 | 0.881 |

## Failure Pattern Analysis

### Incomplete Retrieval

Affected Questions: 15

**Description:** Retrieved context contains insufficient evidence to answer the question completely.

**Remediation:**
1. Increase retrieval top-k to capture more candidate documents
2. Improve document chunking to preserve semantic boundaries  
3. Implement query expansion to find synonymous content
4. Review corpus coverage for underrepresented topics

### Noisy Retrieval

Affected Questions: 8

**Description:** Retrieved documents are present but irrelevant noise dilutes the signal quality.

**Remediation:**
1. Add post-retrieval reranker to filter low-relevance chunks
2. Tune retrieval similarity threshold more conservatively
3. Implement metadata filtering to narrow search scope
4. Consider hybrid retrieval combining BM25 and vector search

### Off-Topic Answer

Affected Questions: 12

**Description:** Model understands context but generates responses that diverge from the question.

**Remediation:**
1. Enforce explicit relevance checking before response generation
2. Improve question understanding through query reformulation
3. Add constraining stop sequences to prevent tangents
4. Increase prompt emphasis on question-focus

### Hallucination Risk

Affected Questions: 6

**Description:** Generated text contains claims not supported by retrieved context.

**Remediation:**
1. Add response grounding constraints to generation prompt
2. Implement fact verification layer comparing output to context
3. Adjust generation temperature for more conservative output
4. Use constrained decoding to force citation of sources

## Summary & Recommendations

- Current average composite score: 0.912
- 52 total questions evaluated
- Bottom 10 questions account for 8.92 points of failure

**Priority Fixes (by estimated impact):**

1. **Retrieval Quality** — Highest leverage; fixing retrieval improves multiple downstream metrics
2. **Reranking Addition** — Moderate effort, significant precision improvement potential
3. **Prompt Engineering** — Low effort, immediate gains in relevancy and hallucination reduction
4. **Test Set Review** — Identify potentially mislabeled questions inflating failure counts
