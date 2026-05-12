# Judge Calibration Report

## Cohen's Kappa Analysis

- Kappa Score: 1.000
- Interpretation: Almost Perfect agreement
- Accuracy: 100.0%
- Test Cases: 10

## Kappa Interpretation Scale

| Range | Interpretation |
|-------|--------|
| 0.81-1.00 | Almost Perfect |
| 0.61-0.80 | Substantial |
| 0.41-0.60 | Moderate |
| 0.21-0.40 | Fair |
| 0.00-0.20 | Slight |
| <0.00 | Poor/Negative |

## Bias Metrics

- Position Bias (A vs B): 40.0% vs 40.0%
- Length Bias: N/A (requires detailed analysis)

## Recommendations

Based on the calibration results, consider:
1. Reviewing disagreement cases for systematic judge errors
2. Refining the judge rubric or prompt if kappa < 0.60
3. Collecting more human labels for validation
4. Monitoring for position bias in production
