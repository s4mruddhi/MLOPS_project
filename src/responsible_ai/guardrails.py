"""
Responsible AI & Prompt Injection Guardrails Engine for RAGOps.
Detects Prompt Injections, Redacts PII, Enforces Access Boundaries, and Audits Input/Output Safety.
"""

import re
from typing import Dict, Any, List, Tuple, Optional

# Known Prompt Injection Signatures & Regex Patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"disregard\s+all\s+prior",
    r"system\s+override",
    r"forget\s+your\s+instructions",
    r"act\s+as\s+root",
    r"pretend\s+you\s+are\s+DAN",
    r"disregard\s+company\s+policy",
    r"bypass\s+access\s+controls",
    r"print\s+system\s+prompt",
    r"reveal\s+secret",
    r"do\s+anything\s+now",
    r"you\s+are\s+now\s+unrestricted",
    r"jailbreak",
]

# Regular expressions for PII (Social Security, Credit Card, API Keys, Private Emails)
SSN_REGEX = r"\b\d{3}-\d{2}-\d{4}\b"
CREDIT_CARD_REGEX = r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
API_KEY_REGEX = r"\b(?:sk|ak|key|secret)_[a-zA-Z0-9]{20,}\b"
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


class ResponsibleAIGuardrail:
    """Enterprise Safety & Compliance Guardrail Engine."""

    def __init__(self, injection_patterns: Optional[List[str]] = None):
        self.injection_patterns = injection_patterns or PROMPT_INJECTION_PATTERNS

    def detect_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detects whether text contains prompt injection or safety bypass patterns."""
        if not text:
            return False, None

        lower_text = text.lower()
        for pattern in self.injection_patterns:
            if re.search(pattern, lower_text, re.IGNORECASE):
                return True, f"Prompt injection pattern detected: '{pattern}'"

        return False, None

    def sanitize_pii(self, text: str) -> Tuple[str, int]:
        """Detects and redacts sensitive PII from text, returning sanitized text and redacted count."""
        if not text:
            return text, 0

        redacted_count = 0

        # Redact SSN
        text, count = re.subn(SSN_REGEX, "[REDACTED_SSN]", text)
        redacted_count += count

        # Redact Credit Cards
        text, count = re.subn(CREDIT_CARD_REGEX, "[REDACTED_CREDIT_CARD]", text)
        redacted_count += count

        # Redact API Keys
        text, count = re.subn(API_KEY_REGEX, "[REDACTED_API_KEY]", text, flags=re.IGNORECASE)
        redacted_count += count

        # Redact Emails
        text, count = re.subn(EMAIL_REGEX, "[REDACTED_EMAIL]", text)
        redacted_count += count

        return text, redacted_count

    def validate_input_prompt(self, query: str, user_role: str = "employee") -> Dict[str, Any]:
        """Validates incoming user prompt against prompt injection and PII leakage."""
        is_injection, violation_reason = self.detect_prompt_injection(query)
        if is_injection:
            return {
                "is_safe": False,
                "sanitized_query": query,
                "violation_type": "PROMPT_INJECTION",
                "reason": violation_reason,
                "pii_redacted_count": 0,
            }

        sanitized_query, pii_count = self.sanitize_pii(query)

        return {
            "is_safe": True,
            "sanitized_query": sanitized_query,
            "violation_type": None,
            "reason": None,
            "pii_redacted_count": pii_count,
        }

    def validate_output_answer(self, answer: str) -> Dict[str, Any]:
        """Validates generated RAG answer for prompt leakage and PII safety."""
        is_injection, violation_reason = self.detect_prompt_injection(answer)
        sanitized_answer, pii_count = self.sanitize_pii(answer)

        return {
            "is_safe": not is_injection,
            "sanitized_answer": sanitized_answer,
            "violation_type": "OUTPUT_LEAKAGE" if is_injection else None,
            "reason": violation_reason,
            "pii_redacted_count": pii_count,
        }
