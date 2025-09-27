"""
Integration tests for the complete research pipeline
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, Mock
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from research.research_orchestrator import ResearchOrchestrator, ResearchQuery
from export.content_formatter import ContentFormatter

@pytest.mark.integration
class TestResearchPipeline:
    """Integration tests for the complete research pipeline"""

    @pytest.fixture
    def mock_api_responses(self):
        """Mock API responses for integration testing"""
        responses = {
            'research_plan': {
                "key_questions": ["What is the topic?", "Why is it important?"],
                "search_strategies": {
                    "keywords": ["keyword1", "keyword2"]
                },
                "source_types": ["academic", "news", "expert"]
            },
            'research_data': {
                "sources": ["Source 1", "Source 2"],
                "findings": ["Finding 1", "Finding 2"]
            },
            'synthesis': {
                "executive_summary": "Test executive summary",
                "key_themes": ["Theme 1", "Theme 2"],
                "supporting_evidence": ["Evidence 1", "Evidence 2"],
                "content_recommendations": {"blog": "Blog recommendation"},
                "actionable_insights": ["Insight 1", "Insight 2"]
            },
            'content': {
                'blog': "# Test Blog Article\n\nThis is test content.",
                'podcast': "PODCAST SCRIPT\n\nHOST: Welcome to the show...",
                'video': "[00:00] Welcome to this video about...",
                'ebook': "# Chapter 1\n\nThis is the first chapter..."
            }
        }
        return responses

    @pytest.mark.asyncio
    async def test_complete_research_pipeline(self, mock_api_responses, temp_dir):
        """Test the complete research pipeline from query to output"""
        # Create research query
        query = ResearchQuery(
            topic="Test Integration Topic",
            focus_areas=["area1", "area2"],
            content_type="blog",
            depth="medium",
            target_audience="general"
        )

        # Mock OpenAI responses
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            # Set up response sequence
            responses = [
                json.dumps(mock_api_responses['research_plan']),
                json.dumps(mock_api_responses['research_data']),
                json.dumps(mock_api_responses['research_data']),  # Second query
                json.dumps(mock_api_responses['synthesis'])
            ]

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_client.chat.completions.create.return_value = mock_response

            # Configure sequential responses
            mock_response.choices[0].message.content = responses[0]

            # Create orchestrator and run research
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                orchestrator = ResearchOrchestrator()

                # Override save method to use temp directory
                original_save = orchestrator.save_research_outputs
                def mock_save(report, query):
                    # Save to temp directory
                    import json
                    report_path = os.path.join(temp_dir, "test_report.json")
                    with open(report_path, 'w') as f:
                        json.dump(report, f, indent=2)
                    return report_path

                orchestrator.save_research_outputs = mock_save

                # Simulate different responses for each API call
                call_count = [0]
                def side_effect(*args, **kwargs):
                    response = Mock()
                    response.choices = [Mock()]
                    response.choices[0].message.content = responses[call_count[0] % len(responses)]
                    call_count[0] += 1
                    return response

                mock_client.chat.completions.create.side_effect = side_effect

                # Run research
                report = await orchestrator.conduct_research(query)

                # Verify report structure
                assert isinstance(report, dict)
                assert "metadata" in report
                assert "executive_summary" in report
                assert "export_formats" in report
                assert report["metadata"]["topic"] == query.topic

    @pytest.mark.asyncio
    async def test_research_to_content_pipeline(self, mock_api_responses, temp_dir):
        """Test pipeline from research report to content generation"""
        # Create a test report file
        test_report = {
            "metadata": {
                "topic": "Test Topic",
                "content_type": "blog",
                "research_depth": "medium",
                "target_audience": "general",
                "generated_at": "2024-01-01T12:00:00",
                "focus_areas": ["area1", "area2"]
            },
            "executive_summary": "Test summary",
            "key_findings": ["Finding 1", "Finding 2"],
            "supporting_evidence": ["Evidence 1"],
            "content_recommendations": {}
        }

        report_path = os.path.join(temp_dir, "test_report.json")
        with open(report_path, 'w') as f:
            json.dump(test_report, f)

        # Test content generation
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_client.chat.completions.create.return_value = mock_response

            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                formatter = ContentFormatter()

                # Test blog generation
                mock_response.choices[0].message.content = mock_api_responses['content']['blog']
                blog_content = formatter.generate_blog_article(test_report)
                assert isinstance(blog_content, str)
                assert "Test Blog Article" in blog_content

                # Test podcast generation
                mock_response.choices[0].message.content = mock_api_responses['content']['podcast']
                podcast_content = formatter.generate_podcast_script(test_report)
                assert isinstance(podcast_content, str)
                assert "PODCAST SCRIPT" in podcast_content

    def test_content_export_pipeline(self, mock_api_responses, temp_dir):
        """Test content export to multiple formats"""
        # Create test report
        test_report = {
            "metadata": {
                "topic": "Export_Test_Topic",
                "content_type": "blog",
                "generated_at": "2024-01-01T12:00:00"
            },
            "executive_summary": "Test summary",
            "key_findings": ["Finding 1", "Finding 2"]
        }

        report_path = os.path.join(temp_dir, "export_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(test_report, f)

        # Mock content generation
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_client.chat.completions.create.return_value = mock_response

            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                formatter = ContentFormatter()

                # Mock all generation methods
                with patch.object(formatter, 'generate_blog_article', return_value=mock_api_responses['content']['blog']):
                    with patch.object(formatter, 'generate_podcast_script', return_value=mock_api_responses['content']['podcast']):
                        with patch.object(formatter, 'generate_video_script', return_value=mock_api_responses['content']['video']):
                            with patch.object(formatter, 'generate_ebook_chapter', return_value=mock_api_responses['content']['ebook']):
                                with patch.object(formatter, 'generate_social_media_content', return_value={"twitter": ["test tweet"]}):
                                    # Export all formats
                                    formatter.export_all_formats(report_path, temp_dir)

                # Verify files were created
                expected_files = [
                    'blog/Export_Test_Topic_*.md',
                    'podcast/Export_Test_Topic_*.md',
                    'video/Export_Test_Topic_*.md',
                    'ebook/Export_Test_Topic_*.md',
                    'social/Export_Test_Topic_*.json'
                ]

                import glob
                for pattern in expected_files:
                    files = glob.glob(os.path.join(temp_dir, pattern))
                    assert len(files) > 0, f"No files found matching pattern: {pattern}"

    @pytest.mark.asyncio
    async def test_error_handling_pipeline(self, temp_dir):
        """Test pipeline error handling"""
        query = ResearchQuery(
            topic="Error Test Topic",
            focus_areas=["area1"],
            content_type="blog",
            depth="medium",
            target_audience="general"
        )

        # Test with API errors
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            # Simulate API error
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                orchestrator = ResearchOrchestrator()

                # Should handle the error gracefully
                with pytest.raises(Exception):
                    await orchestrator.conduct_research(query)

    @pytest.mark.asyncio
    async def test_config_integration(self, temp_dir):
        """Test integration with configuration files"""
        # Create custom config
        config = {
            "research_settings": {
                "default_depth": "deep",
                "max_sources_per_query": 15,
                "fact_check_enabled": True
            },
            "ai_models": {
                "research_model": "gpt-4o",
                "temperature_research": 0.2
            }
        }

        config_path = os.path.join(temp_dir, "research_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Test with custom config
        with patch('openai.OpenAI'):
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                # Mock the config loading to use our test config
                with patch('builtins.open', side_effect=lambda path, *args, **kwargs:
                          open(config_path, *args, **kwargs) if 'research_config.json' in path
                          else open(path, *args, **kwargs)):
                    orchestrator = ResearchOrchestrator()
                    loaded_config = orchestrator.load_config()

                    assert loaded_config["research_settings"]["default_depth"] == "deep"
                    assert loaded_config["ai_models"]["temperature_research"] == 0.2

@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Performance-related integration tests"""

    @pytest.mark.asyncio
    async def test_large_research_query(self, temp_dir):
        """Test handling of large research queries"""
        query = ResearchQuery(
            topic="Large Topic with Many Focus Areas",
            focus_areas=[f"area_{i}" for i in range(20)],  # Many focus areas
            content_type="ebook",
            depth="deep",
            target_audience="professionals"
        )

        # This test would verify the system can handle large queries
        # without running out of memory or timing out
        pass

    def test_concurrent_content_generation(self, temp_dir):
        """Test concurrent content generation"""
        # This test would verify the system can handle multiple
        # content generation requests simultaneously
        pass