# Lab 24 Operations Blueprint

## Executive Summary

This document defines the operational requirements, SLOs, alerting thresholds, incident playbooks, cost projections, and architecture for production deployment of a LAG evaluation and guardrail system.

**Architecture Overview:**

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Monitoring & Cost                                  │
│ └─ Prometheus metrics, cost tracking, usage analytics      │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Orchestration                                      │
│ └─ CI/CD gates, deployment automation, A/B testing          │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Guardrails & Evaluation                           │
│ ├─ Input validation (PII, scope, injection)                │
│ ├─ RAG pipeline (retrieval + generation)                   │
│ └─ Output safety & compliance                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Core Services                                      │
│ ├─ Vector DB (Qdrant/Pinecone)                             │
│ ├─ LLM provider (OpenAI/Groq)                              │
│ └─ Compute (API gateway, load balancer)                    │
└─────────────────────────────────────────────────────────────┘
```

## Service Level Objectives (SLOs)

| Metric | Target | Alert Threshold | Severity | Owner |
|--------|--------|-----------------|----------|-------|
| Availability | 99.5% | <99.0% | P1 | Platform |
| Latency P95 | <150ms | >200ms | P2 | Backend |
| Latency P99 | <300ms | >400ms | P2 | Backend |
| PII Detection Recall | >85% | <80% | P1 | Security |
| Adversarial Detection | >75% | <70% | P1 | Security |
| Output Safety TPR | >80% | <75% | P1 | Safety |
| RAGAS Faithfulness | >0.85 | <0.80 | P2 | ML |
| System Cost/1M queries | <$500 | >$600 | P3 | Finance |

## Alerting Rules

### Critical (P1)

**Alert: PII Detection Failure**
- Condition: Recall drops below 80% in last 24h
- Action: Page on-call security engineer, run audit of recent inputs
- Remediation: Roll back latest PII detection changes, investigate false negatives

**Alert: System Unavailability**
- Condition: Error rate >5% or latency P95 >500ms for >5min
- Action: Immediately escalate to platform team
- Remediation: Check service health, restart if needed, investigate root cause

**Alert: Adversarial Detection Bypassed**
- Condition: Attack detection rate <70% in sampled requests
- Action: Page security team, quarantine affected logs
- Remediation: Review new attack patterns, update detection rules

### High (P2)

**Alert: Latency Degradation**
- Condition: P95 latency >250ms or P99 >400ms for sustained period
- Action: Investigate resource usage, check for slow queries
- Remediation: Profile hot paths, scale if needed, optimize queries

**Alert: Quality Regression**
- Condition: RAGAS faithfulness drops >0.05 from baseline
- Action: Investigate retrieval or generation changes
- Remediation: Revert recent model updates, debug retrieval quality

### Medium (P3)

**Alert: Cost Anomaly**
- Condition: Hourly cost >2x historical average
- Action: Review API usage patterns, check for unusual query volume
- Remediation: Investigate spike, implement rate limiting if needed

## Incident Playbooks

### Scenario 1: Latency Spike to 500ms+

**Detection:** Automated alert when P95 > 500ms for 5 minutes

**Triage (5 min):**
1. Check service health dashboard
2. Review recent deployments or traffic changes
3. Sample logs for error patterns
4. Check Vector DB and LLM provider status

**Mitigation (15 min):**
- Increase input guard thread pool if CPU-bound
- Scale RAG replicas if throughput-bound
- Implement request queuing with adaptive timeout

**Recovery (30 min):**
- Run profiler to identify bottleneck layer
- Optimize slow component (e.g., reranker, embedding lookup)
- Deploy fix with canary rollout (10% → 50% → 100%)

**Post-Incident:**
- Document root cause and prevention strategy
- Add latency SLO alert with tighter threshold
- Review capacity planning

### Scenario 2: PII Detection Bypass (Security Incident)

**Detection:** Customer reports or automated audit finds PII in logs

**Immediate Actions (5 min):**
1. Quarantine affected logs and audit trails
2. Notify security and privacy teams
3. Begin customer notification process

**Triage (15 min):**
1. Determine scope: how many customers affected?
2. Identify pattern: which PII types were missed?
3. Check if Presidio was disabled (common cause)

**Remediation (1 hour):**
- Revert to known-good PII detection patterns
- Enable Presidio if available
- Add regex patterns for newly discovered PII types
- Reprocess historical logs to redact missed PII

**Post-Incident:**
- Conduct security review of detection gaps
- Increase test coverage for edge cases
- Update incident response runbook

### Scenario 3: RAGAS Metric Drop (Quality Regression)

**Detection:** RAGAS faithfulness drops from 0.92 to 0.82 overnight

**Triage (10 min):**
1. Check recent commits to retrieval or generation logic
2. Verify test set hasn't changed
3. Confirm API provider (OpenAI/Groq) isn't degraded
4. Review LLM model changes

**Investigation (30 min):**
- Manually review bottom 10 failing cases
- Check if retrieval top-k was increased (less precision)
- Verify chunking strategy is still optimal
- Test against previous model version

**Remediation:**
- If code change: revert to previous version
- If model change: pin to stable version, coordinate with vendor
- If data change: investigate corpus updates

**Prevention:**
- Add evaluation gate to CI/CD pipeline
- Require pre-deployment quality checks
- Monitor metrics on canary before full rollout

### Scenario 4: Adversarial Attack Exploited

**Detection:** Security team or user reports jailbreak successful

**Immediate (5 min):**
1. Disable or rate-limit the vulnerable endpoint
2. Alert all on-call engineers
3. Begin forensic investigation

**Investigation (30 min):**
1. Replicate the attack and document exact payload
2. Identify which detection layer failed
3. Review recent changes to attack patterns

**Remediation:**
- Add new attack pattern detection rule
- Retrain or recalibrate detection model
- Deploy emergency patch with canary

**Post-Incident:**
- Red-team the system with the discovered attack
- Expand test adversarial inputs
- Review detection accuracy across attack categories

## Deployment & Scaling Strategy

### Progressive Rollout

- **Canary:** 5% traffic, 1 replica, monitor for 2 hours
- **Staged:** 25% traffic, 2 replicas, monitor for 4 hours
- **Ramp:** 75% traffic, 4 replicas, monitor for 2 hours
- **Full:** 100% traffic, 6 replicas, standard monitoring

### Scaling Thresholds

| Metric | Scale Up | Scale Down |
|--------|----------|-----------|
| CPU Usage | >70% | <30% |
| Memory | >75% | <40% |
| Queue Depth | >1000 | <100 |
| Latency P95 | >200ms | <80ms |

### Resource Requirements (Monthly)

- Compute: 6 replicas × 2 CPU × 0.10 $/hour = ~$900/month
- Vector DB: Qdrant managed, 100GB storage = $300/month
- LLM API: 1M queries × $0.001 avg = ~$1,000/month
- Monitoring (Prometheus, Grafana): $200/month
- **Total: ~$2,400/month** or $0.0024 per query

## Maintenance Windows

- **Weekly Review:** Monitor dashboards, review alerts, check SLO compliance
- **Monthly Maintenance:** Update dependencies, run security scans, capacity planning
- **Quarterly Review:** Performance analysis, SLO adjustment, architecture review

## Disaster Recovery

### Backup Strategy

- Daily snapshots of Vector DB (incremental)
- Weekly full exports of evaluation metrics
- Real-time replication to secondary region (if available)
- 30-day retention on all audit logs

### Recovery Time Objectives (RTO)

- **Data loss:** 1 hour (restore from last snapshot)
- **Service unavailability:** 15 minutes (failover to secondary)
- **Partial degradation:** 5 minutes (degrade gracefully, reduce feature set)

### Recovery Procedures

1. **Detect outage:** Automated alert + manual verification
2. **Assess damage:** Check data integrity, identify affected queries
3. **Failover:** Route traffic to backup system or degraded mode
4. **Restore:** Roll back to last known good state
5. **Validate:** Verify system health before full traffic acceptance

## Compliance & Audit

### Data Privacy

- PII is redacted in all logs and audit trails
- Vector embeddings are encrypted at rest
- API keys and credentials are never logged
- Audit logs are immutable and signed

### Compliance Checklist

- ✓ GDPR: PII detection and redaction
- ✓ CCPA: User data minimization and deletion
- ✓ SOC 2: Access controls, audit logging, incident response
- ✓ Industry-specific: HIPAA for medical use cases

### Audit Trail

All requests and responses logged with:
- Timestamp (UTC)
- User ID (anonymized if necessary)
- Input (sanitized, PII redacted)
- Output (safety classification result)
- Latency
- IP address (optional, for abuse detection)

## Cost Optimization

### Strategies

1. **Batch Processing:** Group small queries to amortize overhead
2. **Caching:** Cache frequently asked questions and retrieval results
3. **Model Selection:** Use cheaper models for classification, expensive for generation
4. **Rate Limiting:** Implement tiered pricing and quotas
5. **Reserved Capacity:** Purchase LLM API commitments for 10-20% discount

### Break-Even Analysis

- Fixed costs: ~$1,200/month (infrastructure)
- Variable: $0.001 per query (LLM API)
- Break-even at 120k queries/month
- Typical customer volume: 10-100k queries/month

## Future Roadmap

- **Q2:** Add multi-model judge for improved calibration
- **Q3:** Implement A/B testing framework for model updates
- **Q4:** Deploy federated evaluation for privacy-sensitive customers
- **Q1 next:** Advanced adversarial detection using ML
- **Q2 next:** Multi-language support for guardrails

## Contact & Escalation

| Role | Contact | Escalation |
|------|---------|-----------|
| On-Call Engineer | Pagerduty on-call rotation | Team lead (after 15 min) |
| Security Lead | security@company.com | CISO (critical incidents) |
| Product Owner | product@company.com | VP Product (SLO misses) |
| Finance | finance@company.com | CFO (budget overruns) |
