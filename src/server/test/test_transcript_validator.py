"""
Unit tests for the TranscriptValidator in interview_assisstant_usecase.py.

Tests the dedup, noise filtering, and minimum character/word thresholds
that gate raw STT output before sending to the LLM.
"""
import pytest
import time
import hashlib


# ── Inline TranscriptValidator (extracted for unit testing) ──────────
# This mirrors the exact logic from interview_assisstant_usecase.py
# to allow testing without importing the full usecase (which has heavy deps).

class TranscriptValidator:
    """Validate raw STT output before sending to LLM."""

    NOISE_WORDS = frozenset([
        "", "the", "a", "an", "um", "uh", "ah", "oh", "huh",
        "hmm", "yeah", "yes", "no", "okay", "ok",
    ])
    MIN_CHARS = 10
    MIN_WORDS = 2
    DEDUP_TTL = 30.0

    def __init__(self):
        self._seen: dict[str, float] = {}

    def clear_cache(self):
        self._seen.clear()

    def _evict(self):
        now = time.monotonic()
        expired = [k for k, t in self._seen.items() if now - t > self.DEDUP_TTL]
        for k in expired:
            del self._seen[k]

    def is_valid(self, text: str) -> tuple[bool, str]:
        if not text or not text.strip():
            return False, "empty"

        cleaned = text.strip().lower()

        # Noise word check
        if cleaned in self.NOISE_WORDS:
            return False, "noise_word"

        # Length checks
        if len(cleaned) < self.MIN_CHARS:
            return False, "too_short_chars"

        words = cleaned.split()
        if len(words) < self.MIN_WORDS:
            return False, "too_few_words"

        # Dedup
        self._evict()
        sig = hashlib.md5(cleaned.encode()).hexdigest()
        if sig in self._seen:
            return False, "duplicate"
        self._seen[sig] = time.monotonic()

        return True, "ok"


# ── Tests ────────────────────────────────────────────────────────────

class TestTranscriptValidator:
    """Unit tests for TranscriptValidator."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.v = TranscriptValidator()

    # ── Empty/whitespace ─────────────────────────────
    @pytest.mark.parametrize("text", ["", "   ", None])
    def test_empty_rejected(self, text):
        ok, reason = self.v.is_valid(text)
        assert not ok
        assert reason == "empty"

    # ── Noise words ──────────────────────────────────
    @pytest.mark.parametrize("text", ["um", "uh", "the", "okay", "yes", "no"])
    def test_noise_words_rejected(self, text):
        ok, reason = self.v.is_valid(text)
        assert not ok
        assert reason == "noise_word"

    # ── Too short ────────────────────────────────────
    def test_too_short_chars(self):
        ok, reason = self.v.is_valid("hi there")  # 8 chars
        assert not ok
        assert reason == "too_short_chars"

    def test_too_few_words(self):
        ok, reason = self.v.is_valid("helloworld1")  # 1 word, 11 chars
        assert not ok
        assert reason == "too_few_words"

    # ── Valid input ──────────────────────────────────
    def test_valid_input_accepted(self):
        ok, reason = self.v.is_valid("tell me about your experience with Python")
        assert ok
        assert reason == "ok"

    # ── Dedup ────────────────────────────────────────
    def test_duplicate_rejected(self):
        text = "tell me about your experience with FastAPI"
        ok1, _ = self.v.is_valid(text)
        ok2, reason2 = self.v.is_valid(text)
        assert ok1 is True
        assert ok2 is False
        assert reason2 == "duplicate"

    def test_case_insensitive_dedup(self):
        ok1, _ = self.v.is_valid("What is your greatest strength?")
        ok2, reason2 = self.v.is_valid("what is your greatest strength?")
        assert ok1 is True
        assert ok2 is False
        assert reason2 == "duplicate"

    # ── Cache clear ──────────────────────────────────
    def test_clear_cache_allows_resubmission(self):
        text = "describe your team collaboration style"
        self.v.is_valid(text)
        self.v.clear_cache()
        ok, reason = self.v.is_valid(text)
        assert ok
        assert reason == "ok"

    # ── Edge cases ───────────────────────────────────
    def test_just_above_threshold(self):
        # 10 chars, 2 words
        ok, reason = self.v.is_valid("hello test")
        assert ok
        assert reason == "ok"
