"""
pytest configuration and shared fixtures for DeepMeet-Guard tests.
"""
import pytest
import sys
import os

# Ensure the src directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def sample_user_info():
    """Return a sample UserInfo dict for testing."""
    return {
        "name": "Test User",
        "role": "Backend Developer",
        "skills": ["Python", "FastAPI"],
        "experience": ["Developer at TestCorp (2023-2024)"],
        "education": "BSc CS",
        "projects": ["Test Project"],
        "strengths": ["Problem solving"],
        "weaknesses": ["Over-engineering"],
    }


@pytest.fixture
def sample_org_info():
    """Return a sample OrganizationInfo dict for testing."""
    return {
        "company": "TestCorp",
        "industry": "Technology",
        "tech_stack": ["Python", "Docker"],
        "role": "Backend Engineer",
        "responsibilities": ["Build APIs"],
    }
