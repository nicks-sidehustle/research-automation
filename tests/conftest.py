"""
Pytest configuration and shared fixtures for research automation tests
"""

import os
import sys
import json
import tempfile
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_research_query():
    """Sample research query for testing"""
    from research.research_orchestrator import ResearchQuery
    return ResearchQuery(
        topic="Test Topic",
        focus_areas=["area1", "area2"],
        content_type="blog",
        depth="medium",
        target_audience="general"
    )

@pytest.fixture
def sample_research_report():
    """Sample research report data for testing"""
    return {
        "metadata": {
            "topic": "Test Topic",
            "content_type": "blog",
            "research_depth": "medium",
            "target_audience": "general",
            "generated_at": "2024-01-01T12:00:00",
            "focus_areas": ["area1", "area2"]
        },
        "executive_summary": "This is a test summary",
        "key_findings": [
            "Finding 1",
            "Finding 2",
            "Finding 3"
        ],
        "supporting_evidence": [
            "Evidence 1",
            "Evidence 2"
        ],
        "content_recommendations": {
            "blog_ready": {
                "title": "Test Blog Title",
                "outline": ["Section 1", "Section 2"]
            }
        },
        "export_formats": {
            "blog_ready": {
                "title": "Test Blog Title",
                "subtitle": "Test subtitle",
                "outline": ["Section 1", "Section 2"],
                "call_to_action": "Learn more",
                "seo_keywords": ["keyword1", "keyword2"]
            },
            "podcast_script": {
                "episode_title": "Test Episode",
                "intro_hook": "Test hook",
                "main_segments": ["Segment 1", "Segment 2"]
            }
        }
    }

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('openai.OpenAI') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"test": "response"}'

        mock_client.return_value.chat.completions.create.return_value = mock_response
        yield mock_client

@pytest.fixture
def config_file(temp_dir):
    """Create a temporary config file"""
    config = {
        "research_settings": {
            "default_depth": "medium",
            "max_sources_per_query": 5,
            "fact_check_enabled": True
        },
        "ai_models": {
            "research_model": "gpt-4o",
            "temperature_research": 0.3
        }
    }

    config_path = os.path.join(temp_dir, "research_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f)

    return config_path

@pytest.fixture
def sample_report_file(temp_dir, sample_research_report):
    """Create a sample report file for testing"""
    report_path = os.path.join(temp_dir, "test_report.json")
    with open(report_path, 'w') as f:
        json.dump(sample_research_report, f)
    return report_path

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    original_env = os.environ.copy()
    os.environ['OPENAI_API_KEY'] = 'test-key'
    yield
    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing"""
    with patch('builtins.open', mock_open()) as mock_file:
        yield mock_file

def mock_open(read_data=""):
    """Helper function to create mock file operations"""
    from unittest.mock import mock_open as original_mock_open
    return original_mock_open(read_data=read_data)