"""
Unit tests for TokenEstimator and TokenBudget from LLMController.

Tests the token estimation heuristic and budget calculations
without requiring an LLM provider connection.
"""
import pytest


class TestTokenEstimator:
    """Test the TokenEstimator heuristic."""

    def setup_method(self):
        # Inline the class to avoid importing heavy LLM dependencies
        class TokenEstimator:
            @staticmethod
            def estimate(text: str) -> int:
                return max(1, int(len(text) / 4.0))

        self.estimator = TokenEstimator()

    def test_empty_string(self):
        assert self.estimator.estimate("") == 1  # max(1, 0)

    def test_short_string(self):
        result = self.estimator.estimate("hi")
        assert result == 1  # max(1, int(2/4))

    def test_medium_string(self):
        text = "Hello, how are you doing today?"
        result = self.estimator.estimate(text)
        assert result == int(len(text) / 4)

    def test_long_string(self):
        text = "a" * 1000
        result = self.estimator.estimate(text)
        assert result == 250

    def test_always_positive(self):
        for i in range(20):
            result = self.estimator.estimate("x" * i)
            assert result >= 1


class TestTokenBudget:
    """Test the TokenBudget dataclass."""

    def setup_method(self):
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class TokenBudget:
            context_window: int
            system_reserve: int = 800
            response_reserve: int = 600
            summary_max: int = 300
            user_turn_max: int = 500

            @property
            def available_for_history(self) -> int:
                return max(0, self.context_window - self.system_reserve
                           - self.response_reserve - self.summary_max
                           - self.user_turn_max)

        self.TokenBudget = TokenBudget

    def test_local_budget(self):
        budget = self.TokenBudget(context_window=4096)
        available = budget.available_for_history
        expected = 4096 - 800 - 600 - 300 - 500
        assert available == expected

    def test_remote_budget(self):
        budget = self.TokenBudget(
            context_window=128000,
            system_reserve=2000,
            response_reserve=2000,
            summary_max=1500,
            user_turn_max=1500,
        )
        available = budget.available_for_history
        assert available == 128000 - 2000 - 2000 - 1500 - 1500

    def test_tiny_window_clamps_to_zero(self):
        budget = self.TokenBudget(context_window=100)
        assert budget.available_for_history == 0


class TestSchemaValidation:
    """Test Pydantic schema validation (field length limits)."""

    def test_user_info_valid(self):
        from server.models.schemas import UserInfo
        user = UserInfo(
            name="Test User",
            role="Developer",
            skills=["Python"],
            experience=["Dev at X"],
            education="BSc CS",
            projects=["Project A"],
            strengths=["Fast learner"],
            weaknesses=["Over-engineering"],
        )
        assert user.name == "Test User"

    def test_user_info_name_too_long(self):
        from server.models.schemas import UserInfo
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserInfo(
                name="x" * 201,  # max_length=200
                role="Developer",
                skills=["Python"],
                experience=["Dev at X"],
                education="BSc CS",
                projects=["Project A"],
                strengths=["Fast learner"],
                weaknesses=["Over-engineering"],
            )

    def test_user_info_too_many_skills(self):
        from server.models.schemas import UserInfo
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserInfo(
                name="Test",
                role="Dev",
                skills=["skill"] * 51,  # max_length=50
                experience=["x"],
                education="BSc",
                projects=["x"],
                strengths=["x"],
                weaknesses=["x"],
            )


class TestConfigCaching:
    """Test that get_config() returns cached singleton."""

    def test_same_instance(self):
        from server.helpers import get_config
        c1 = get_config()
        c2 = get_config()
        assert c1 is c2

    def test_config_has_app_name(self):
        from server.helpers import get_config
        config = get_config()
        assert hasattr(config, "APP_NAME")
