"""Input validation guardrails: PII detection, scope filtering, injection blocking."""

from __future__ import annotations

import os
import re
import statistics
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent
load_dotenv(ROOT / ".env")


class InputValidator:
    """Multi-layer input validation and sanitization."""
    
    # Layer 1: PII Detection Patterns
    PII_DETECTORS = {
        "EMAIL": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "PHONE_US": re.compile(r'(?<!\d)(?:\+?1[-.]?)?(?:\(\d{3}\)[-.]?)?\d{3}[-.]?\d{4}(?!\d)'),
        "PHONE_VN": re.compile(r'(?<!\d)(?:\+84|0)(?:[1-9]\d{1}|\d)[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?!\d)'),
        "SSN_PATTERN": re.compile(r'(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)'),
        "CREDIT_CARD": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        "VN_ID": re.compile(r'(?<!\d)\d{12}(?!\d)'),
    }
    
    # Layer 2: Injection Attack Patterns
    ATTACK_PATTERNS = {
        "ignore_instructions": re.compile(r'\bignore\b.{0,50}instructions\b', re.I),
        "system_prompt": re.compile(r'system prompt|system message|hidden instruction', re.I),
        "jailbreak_tokens": re.compile(r'\b(?:DAN|do anything now|unrestricted)\b', re.I),
        "role_escape": re.compile(r'(?:pretend|act as|roleplay as).{0,30}(?:evil|unrestricted|without)', re.I),
        "base64_decode": re.compile(r'base64|decode|encode|cipher', re.I),
    }
    
    # Layer 3: Scope Validation Keywords
    ALLOWED_SCOPES = {
        "retrieval": ["retrieve", "search", "context", "chunk", "embedding", "bm25"],
        "evaluation": ["evaluate", "metric", "score", "ragas", "faithfulness"],
        "guardrail": ["safety", "pii", "guard", "filter", "block"],
        "judge": ["judge", "compare", "pairwise", "kappa", "rubric"],
        "latency": ["latency", "p50", "p95", "benchmark", "performance"],
        "production": ["slo", "alert", "incident", "deploy", "cost"],
    }
    
    def __init__(self):
        self._presidio_available = False
        self._test_presidio()
    
    def _test_presidio(self) -> None:
        """Check if Presidio is available."""
        if os.getenv("USE_PRESIDIO", "false").strip().lower() in {"1", "true", "yes"}:
            try:
                from presidio_analyzer import AnalyzerEngine
                self._presidio_available = True
            except ImportError:
                pass
    
    def detect_pii(self, text: str) -> tuple[list[str], str]:
        """Detect PII in text and return sanitized version."""
        
        pii_types = []
        sanitized = text
        
        # Regex-based detection
        for pii_type, pattern in self.PII_DETECTORS.items():
            if pattern.search(sanitized):
                pii_types.append(pii_type)
                sanitized = pattern.sub(f"[{pii_type}]", sanitized)
        
        return pii_types, sanitized
    
    def detect_injection(self, text: str) -> tuple[bool, str]:
        """Detect prompt injection or jailbreak attempts."""
        
        for attack_type, pattern in self.ATTACK_PATTERNS.items():
            if pattern.search(text):
                return True, attack_type
        
        return False, ""
    
    def validate_scope(self, text: str) -> tuple[bool, str]:
        """Check if input is within Lab 24 scope."""
        
        if not text.strip():
            return False, "empty"
        
        text_lower = text.lower()
        scope_scores = {}
        
        for scope, keywords in self.ALLOWED_SCOPES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scope_scores[scope] = score
        
        max_scope = max(scope_scores, key=scope_scores.get)
        max_score = scope_scores[max_scope]
        
        if max_score > 0:
            return True, max_scope
        else:
            return False, "out_of_scope"
    
    def sanitize_input(self, user_input: str) -> dict:
        """Full input validation pipeline."""
        
        start_time = time.perf_counter()
        
        # Truncate for safety
        original = (user_input or "")[:5000]
        
        # Layer 1: PII detection
        pii_list, sanitized_text = self.detect_pii(original)
        
        # Layer 2: Injection detection
        is_attack, attack_reason = self.detect_injection(original)
        
        # Layer 3: Scope validation
        in_scope, scope_reason = self.validate_scope(sanitized_text)
        
        # Block decision
        is_blocked = is_attack or (not in_scope) or (not original.strip())
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "input": original,
            "sanitized": sanitized_text,
            "pii_detected": pii_list,
            "pii_count": len(pii_list),
            "injection_detected": is_attack,
            "injection_type": attack_reason,
            "in_scope": in_scope,
            "scope_type": scope_reason,
            "blocked": is_blocked,
            "block_reason": "injection" if is_attack else ("out_of_scope" if not in_scope else "empty"),
            "latency_ms": round(elapsed_ms, 3),
        }


def run_pii_tests() -> None:
    """Test PII detection on diverse inputs."""
    
    print("🛡️  Input Validator: PII Detection Tests")
    print("-" * 60)
    
    validator = InputValidator()
    
    test_cases = [
        "My email is alice@company.com and phone is +1-555-123-4567. Help with RAG evaluation.",
        "Contact: john.doe@example.org, 555.987.6543. Question about guardrails?",
        "Vietnamese number 0912345678, email test@domain.vn. How do guardrails work?",
        "CCCD: 123456789012. PII detection question?",
        "Credit card 1234-5678-9012-3456. Latency benchmark?",
        "Normal question about retrieval and evaluation metrics without PII.",
        "",
        "A very long normal question " * 200,
        "Email: contact@lab24.edu, phone: +84 123 456 789. Explain faithfulness in RAGAS.",
        "Multiple PII: john@test.com, 5551234567, ID 098765432109. Tell me about CI/CD gates.",
    ]
    
    results = []
    detected_count = 0
    latencies = []
    
    for test in test_cases:
        result = validator.sanitize_input(test)
        latencies.append(result["latency_ms"])
        
        if result["pii_detected"]:
            detected_count += 1
        
        results.append({
            "input": test[:50],
            "pii_detected": ",".join(result["pii_detected"]),
            "pii_count": result["pii_count"],
            "injection": result["injection_detected"],
            "in_scope": result["in_scope"],
            "blocked": result["blocked"],
            "latency_ms": result["latency_ms"],
        })
    
    # Calculate stats
    recall = detected_count / 6  # 6 cases have PII
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
    
    # Save results
    df = pd.DataFrame(results)
    output_file = PHASE_DIR / "pii_test_results.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✓ Tested {len(test_cases)} inputs")
    print(f"✓ Detected PII in {detected_count} inputs (recall: {recall:.0%})")
    print(f"✓ P95 Latency: {p95:.2f}ms")
    print(f"✓ Saved results → {output_file}")


def run_scope_tests() -> None:
    """Test scope validation."""
    
    print("\n🎯 Input Validator: Scope Validation Tests")
    print("-" * 60)
    
    validator = InputValidator()
    
    in_scope_tests = [
        "How does RAG retrieval work?",
        "Explain RAGAS faithfulness metric.",
        "What are common guardrail patterns?",
        "How do you measure latency P95?",
        "Design an LLM judge rubric.",
    ]
    
    out_of_scope_tests = [
        "What's the weather today?",
        "Tell me a joke.",
        "Translate this to French.",
        "Cook me a recipe.",
        "Plan a vacation.",
    ]
    
    results = []
    correct = 0
    
    for test in in_scope_tests:
        result = validator.validate_scope(test)
        in_scope, scope = result
        correct += int(in_scope)
        results.append({"input": test, "expected": True, "predicted": in_scope, "scope": scope})
    
    for test in out_of_scope_tests:
        result = validator.validate_scope(test)
        in_scope, scope = result
        correct += int(not in_scope)
        results.append({"input": test, "expected": False, "predicted": in_scope, "scope": scope})
    
    accuracy = correct / len(results)
    
    df = pd.DataFrame(results)
    output_file = PHASE_DIR / "topic_guard_results.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✓ Tested {len(results)} inputs")
    print(f"✓ Accuracy: {accuracy:.0%}")
    print(f"✓ Saved results → {output_file}")


if __name__ == "__main__":
    run_pii_tests()
    run_scope_tests()
