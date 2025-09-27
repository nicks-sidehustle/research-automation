"""
Unit tests for Research Orchestrator
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from research.research_orchestrator import ResearchOrchestrator, ResearchQuery

class TestResearchOrchestrator:
    """Test cases for ResearchOrchestrator class"""

    @pytest.fixture
    def orchestrator(self, mock_openai_client):
        """Create orchestrator instance with mocked dependencies"""
        with patch('research.research_orchestrator.os.getenv', return_value='test-key'):
            return ResearchOrchestrator()

    def test_init(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'openai_client')
        assert hasattr(orchestrator, 'config')

    def test_load_config_file_not_found(self, orchestrator):
        """Test config loading when file doesn't exist"""
        config = orchestrator.load_config()
        assert isinstance(config, dict)
        assert 'default_depth' in config
        assert config['default_depth'] == 'medium'

    @patch('builtins.open')
    @patch('json.load')
    def test_load_config_file_exists(self, mock_json_load, mock_open, orchestrator):
        """Test config loading when file exists"""
        mock_config = {"test": "config"}
        mock_json_load.return_value = mock_config

        config = orchestrator.load_config()
        assert config == mock_config

    @pytest.mark.asyncio
    async def test_generate_research_plan(self, orchestrator, sample_research_query, mock_openai_client):
        """Test research plan generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"key_questions": ["Q1", "Q2"]}'

        orchestrator.openai_client.chat.completions.create.return_value = mock_response

        result = await orchestrator.generate_research_plan(sample_research_query)

        assert isinstance(result, dict)
        assert "key_questions" in result
        orchestrator.openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_research_plan_invalid_json(self, orchestrator, sample_research_query):
        """Test research plan generation with invalid JSON response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'invalid json'

        orchestrator.openai_client.chat.completions.create.return_value = mock_response

        result = await orchestrator.generate_research_plan(sample_research_query)

        assert "error" in result

    @pytest.mark.asyncio
    async def test_simulate_research_query(self, orchestrator):
        """Test simulated research query"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"sources": ["source1"], "findings": ["finding1"]}'

        orchestrator.openai_client.chat.completions.create.return_value = mock_response

        result = await orchestrator.simulate_research_query("test query")

        assert isinstance(result, dict)
        assert "sources" in result or "findings" in result

    @pytest.mark.asyncio
    async def test_gather_research_data(self, orchestrator):
        """Test research data gathering"""
        research_plan = {
            "search_strategies": {
                "keywords": ["keyword1", "keyword2"]
            }
        }

        with patch.object(orchestrator, 'simulate_research_query', new_callable=AsyncMock) as mock_simulate:
            mock_simulate.return_value = {
                "sources": ["source1"],
                "findings": ["finding1"]
            }

            result = await orchestrator.gather_research_data(research_plan)

            assert isinstance(result, dict)
            assert "sources" in result
            assert "key_findings" in result

    @pytest.mark.asyncio
    async def test_synthesize_findings(self, orchestrator, sample_research_query):
        """Test findings synthesis"""
        research_data = {
            "sources": ["source1"],
            "key_findings": ["finding1"],
            "statistics": ["stat1"]
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"executive_summary": "test summary"}'

        orchestrator.openai_client.chat.completions.create.return_value = mock_response

        result = await orchestrator.synthesize_findings(research_data, sample_research_query)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_report(self, orchestrator, sample_research_query):
        """Test report generation"""
        synthesis = {
            "executive_summary": "Test summary",
            "key_themes": ["theme1", "theme2"],
            "supporting_evidence": ["evidence1"],
            "content_recommendations": {"blog": "recommendation"},
            "actionable_insights": ["insight1"]
        }

        result = await orchestrator.generate_report(synthesis, sample_research_query)

        assert isinstance(result, dict)
        assert "metadata" in result
        assert "executive_summary" in result
        assert "export_formats" in result
        assert result["metadata"]["topic"] == sample_research_query.topic

    def test_format_for_blog(self, orchestrator, sample_research_query):
        """Test blog formatting"""
        synthesis = {
            "executive_summary": "Test summary",
            "key_themes": ["theme1", "theme2"]
        }

        result = orchestrator.format_for_blog(synthesis, sample_research_query)

        assert isinstance(result, dict)
        assert "title" in result
        assert "subtitle" in result
        assert "outline" in result

    def test_format_for_podcast(self, orchestrator, sample_research_query):
        """Test podcast formatting"""
        synthesis = {
            "executive_summary": "Test summary",
            "key_themes": ["theme1", "theme2"],
            "actionable_insights": ["insight1"]
        }

        result = orchestrator.format_for_podcast(synthesis, sample_research_query)

        assert isinstance(result, dict)
        assert "episode_title" in result
        assert "intro_hook" in result
        assert "main_segments" in result

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=lambda: pytest.mock_open())
    def test_save_research_outputs(self, mock_open, mock_makedirs, orchestrator, sample_research_report, sample_research_query):
        """Test saving research outputs"""
        orchestrator.save_research_outputs(sample_research_report, sample_research_query)

        mock_makedirs.assert_called()
        mock_open.assert_called()

    def test_generate_markdown_summary(self, orchestrator, sample_research_report):
        """Test markdown summary generation"""
        result = orchestrator.generate_markdown_summary(sample_research_report)

        assert isinstance(result, str)
        assert "# Research Report:" in result
        assert "## Executive Summary" in result
        assert "## Key Findings" in result

class TestResearchQuery:
    """Test cases for ResearchQuery dataclass"""

    def test_research_query_creation(self):
        """Test ResearchQuery creation"""
        query = ResearchQuery(
            topic="Test Topic",
            focus_areas=["area1", "area2"],
            content_type="blog",
            depth="medium",
            target_audience="general"
        )

        assert query.topic == "Test Topic"
        assert query.focus_areas == ["area1", "area2"]
        assert query.content_type == "blog"
        assert query.depth == "medium"
        assert query.target_audience == "general"