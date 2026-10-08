def redact(text: str) -> str:
    for key in ("Authorization:", "token=", "password=", "secret="):
        text = text.replace(key, "[REDACTED]:")
    return text

def test_redaction():
    assert "password=[REDACTED]" in redact("password=foo")
