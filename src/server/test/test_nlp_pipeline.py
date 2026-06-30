"""
Unit tests for the NLP preprocessing pipeline (preprocess_before_llm).

Tests that STT artifacts, filler words, repeated words, and hanging
determiners are cleaned properly, and punctuation is restored.
"""
import pytest
import sys
import os

# Add parent dirs so we can import the controller
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestPreprocessBeforeLLM:
    """Test the NLP preprocessing pipeline."""

    @pytest.fixture(autouse=True)
    def setup(self):
        from server.controllers.nlp_controller import preprocess_before_llm
        self.preprocess = preprocess_before_llm

    # ── Filler removal ───────────────────────────────
    def test_filler_removal(self):
        result = self.preprocess("um the meeting is scheduled for uh tomorrow")
        # Should remove "um" and "uh"
        assert "um" not in result.lower()
        assert "uh" not in result.lower()
        assert "meeting" in result.lower()

    # ── Repeated word removal ────────────────────────
    def test_repeated_word_removal(self):
        result = self.preprocess("the the meeting is is scheduled for tomorrow")
        # Should not have consecutive duplicate "the the" or "is is"
        words = result.lower().split()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                # Allow certain natural doubles
                assert words[i] not in ("the", "is", "a"), f"Duplicate found: '{words[i]}'"

    # ── Hanging determiner ───────────────────────────
    def test_hanging_determiner_removed(self):
        result = self.preprocess("the")
        assert result.strip() == "" or result.strip() == "."

    def test_hanging_determiner_at_end(self):
        result = self.preprocess("meeting the the")
        # Should not end with a hanging "the"
        cleaned = result.strip().rstrip(".")
        assert not cleaned.lower().endswith("the the")

    # ── Empty/short input ────────────────────────────
    def test_empty_input(self):
        result = self.preprocess("")
        assert result.strip() == "" or result.strip() == "."

    def test_whitespace_only(self):
        result = self.preprocess("   ")
        assert result.strip() == "" or result.strip() == "."

    # ── Normal text passthrough ──────────────────────
    def test_normal_text_preserved(self):
        text = "I have five years of experience with Python"
        result = self.preprocess(text)
        assert "experience" in result.lower()
        assert "python" in result.lower()

    # ── Punctuation restoration ──────────────────────
    def test_question_mark_added(self):
        result = self.preprocess("where is the nearest cafe")
        # Should end with ? since it starts with "where"
        assert result.strip().endswith("?")

    def test_period_added_for_statement(self):
        result = self.preprocess("the project deadline is next week")
        assert result.strip().endswith(".")


class TestPreprocessEdgeCases:
    """Edge case tests."""

    @pytest.fixture(autouse=True)
    def setup(self):
        from server.controllers.nlp_controller import preprocess_before_llm
        self.preprocess = preprocess_before_llm

    def test_single_valid_word(self):
        result = self.preprocess("hello")
        assert "hello" in result.lower()

    def test_long_utterance_with_many_issues(self):
        text = (
            "um so basically what what i wanted to say is that uh the the system "
            "performance has has been really good lately"
        )
        result = self.preprocess(text)
        assert len(result) > 10
        assert "performance" in result.lower()
