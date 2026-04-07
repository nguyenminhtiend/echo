from src.gateway.scrubber import scrub_pii, scrub_secrets


def test_scrub_email():
    text = "Contact john@example.com for details"
    result = scrub_pii(text)
    assert "john@example.com" not in result
    assert "<EMAIL>" in result


def test_scrub_phone():
    text = "Call me at 555-123-4567"
    result = scrub_pii(text)
    assert "555-123-4567" not in result


def test_scrub_aws_key():
    text = "key is AKIAIOSFODNN7EXAMPLE"
    result = scrub_secrets(text)
    assert "AKIAIOSFODNN7EXAMPLE" not in result
    assert "<SECRET>" in result


def test_scrub_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    result = scrub_secrets(f"token: {jwt}")
    assert jwt not in result
    assert "<SECRET>" in result


def test_no_false_positives():
    text = "This is a normal sentence about coding."
    assert scrub_pii(text) == text
    assert scrub_secrets(text) == text
