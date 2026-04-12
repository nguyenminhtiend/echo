import re
from functools import lru_cache

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Use en_core_web_sm (~12MB) instead of Presidio's default en_core_web_lg (~500MB).
# The small model is sufficient for entity detection used here (email, phone, SSN).
_NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}


@lru_cache(maxsize=1)
def _get_analyzer() -> AnalyzerEngine:
    nlp_engine = NlpEngineProvider(nlp_configuration=_NLP_CONFIG).create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


# Regex patterns for secrets
_SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key
    re.compile(r"(?:aws.{0,20})?['\"][0-9a-zA-Z/+]{40}['\"]"),  # AWS secret key
    re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),  # JWT
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),  # Private keys
    re.compile(r"ghp_[0-9a-zA-Z]{36}"),  # GitHub PAT
    re.compile(r"sk-[0-9a-zA-Z]{48}"),  # OpenAI API key
    re.compile(r"sk-ant-[0-9a-zA-Z-]{90,}"),  # Anthropic API key
]


def scrub_pii(text: str) -> str:
    """Replace PII (emails, phones, SSNs) with placeholders using Presidio."""
    results = _get_analyzer().analyze(
        text=text,
        entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN"],
        language="en",
    )
    # Sort by start position descending to replace from end
    for result in sorted(results, key=lambda r: r.start, reverse=True):
        entity_tag = result.entity_type.replace("_ADDRESS", "").replace("US_", "")
        text = text[: result.start] + f"<{entity_tag}>" + text[result.end :]
    return text


def scrub_secrets(text: str) -> str:
    """Replace secret patterns (AWS keys, JWTs, private keys) with <SECRET>."""
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("<SECRET>", text)
    return text


def scrub_all(text: str) -> str:
    """Run both PII and secret scrubbing."""
    return scrub_secrets(scrub_pii(text))
