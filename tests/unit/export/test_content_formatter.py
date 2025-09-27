"""
Unit tests for Content Formatter
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, mock_open

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from export.content_formatter import ContentFormatter

class TestContentFormatter:
    """Test cases for ContentFormatter class"""

    @pytest.fixture
    def formatter(self, mock_openai_client):
        """Create formatter instance with mocked dependencies"""
        with patch('export.content_formatter.os.getenv', return_value='test-key'):
            return ContentFormatter()

    def test_init(self, formatter):
        """Test formatter initialization"""
        assert formatter is not None
        assert hasattr(formatter, 'openai_client')

    def test_load_research_report(self, formatter, sample_report_file):
        """Test loading research report from file"""
        result = formatter.load_research_report(sample_report_file)

        assert isinstance(result, dict)
        assert "metadata" in result
        assert "executive_summary" in result

    def test_generate_blog_article(self, formatter, sample_research_report):
        """Test blog article generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "# Test Blog Article\n\nContent here..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_blog_article(sample_research_report)

        assert isinstance(result, str)
        assert "Test Blog Article" in result
        formatter.openai_client.chat.completions.create.assert_called_once()

    def test_generate_blog_article_with_style(self, formatter, sample_research_report):
        """Test blog article generation with specific style"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "# Conversational Blog\n\nFriendly content..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_blog_article(sample_research_report, style="conversational")

        assert isinstance(result, str)
        call_args = formatter.openai_client.chat.completions.create.call_args
        assert "conversational" in call_args[1]["messages"][0]["content"]

    def test_generate_podcast_script(self, formatter, sample_research_report):
        """Test podcast script generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "PODCAST SCRIPT\n[INTRO MUSIC]\nHOST: Welcome..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_podcast_script(sample_research_report)

        assert isinstance(result, str)
        assert "PODCAST SCRIPT" in result

    def test_generate_podcast_script_with_hosts(self, formatter, sample_research_report):
        """Test podcast script generation with multiple hosts"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "HOST1: Hello\nHOST2: Welcome back"

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_podcast_script(sample_research_report, hosts=["Host1", "Host2"])

        assert isinstance(result, str)
        call_args = formatter.openai_client.chat.completions.create.call_args
        assert "Host1, Host2" in call_args[1]["messages"][0]["content"]

    def test_generate_video_script(self, formatter, sample_research_report):
        """Test video script generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "[00:00] INTRO\n[SHOW: Title card]\nHello everyone..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_video_script(sample_research_report)

        assert isinstance(result, str)
        assert "[00:00]" in result

    def test_generate_video_script_custom_duration(self, formatter, sample_research_report):
        """Test video script generation with custom duration"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Short video content"

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_video_script(sample_research_report, duration=300)

        call_args = formatter.openai_client.chat.completions.create.call_args
        assert "300-second" in call_args[1]["messages"][0]["content"]

    def test_generate_ebook_chapter(self, formatter, sample_research_report):
        """Test ebook chapter generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "# Chapter 1\n\n## Introduction\nChapter content..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_ebook_chapter(sample_research_report)

        assert isinstance(result, str)
        assert "Chapter" in result

    def test_generate_ebook_chapter_with_number(self, formatter, sample_research_report):
        """Test ebook chapter generation with specific chapter number"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "# Chapter 5\n\nContent..."

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_ebook_chapter(sample_research_report, chapter_number=5)

        call_args = formatter.openai_client.chat.completions.create.call_args
        assert "Chapter 5" in call_args[1]["messages"][0]["content"]

    def test_generate_social_media_content(self, formatter, sample_research_report):
        """Test social media content generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "twitter": ["Tweet 1", "Tweet 2"],
            "linkedin": ["LinkedIn post 1"],
            "instagram": ["Instagram post 1"],
            "youtube_shorts": ["Short concept 1"]
        })

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_social_media_content(sample_research_report)

        assert isinstance(result, dict)
        assert "twitter" in result
        assert "linkedin" in result
        assert "instagram" in result
        assert "youtube_shorts" in result

    def test_generate_social_media_content_invalid_json(self, formatter, sample_research_report):
        """Test social media content generation with invalid JSON"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "invalid json"

        formatter.openai_client.chat.completions.create.return_value = mock_response

        result = formatter.generate_social_media_content(sample_research_report)

        assert isinstance(result, dict)
        assert "error" in result

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_all_formats(self, mock_file, mock_makedirs, formatter, sample_report_file):
        """Test exporting all content formats"""
        # Mock all the generation methods
        with patch.object(formatter, 'generate_blog_article', return_value="Blog content"):
            with patch.object(formatter, 'generate_podcast_script', return_value="Podcast script"):
                with patch.object(formatter, 'generate_video_script', return_value="Video script"):
                    with patch.object(formatter, 'generate_ebook_chapter', return_value="Ebook chapter"):
                        with patch.object(formatter, 'generate_social_media_content', return_value={"twitter": ["tweet"]}):
                            formatter.export_all_formats(sample_report_file)

        # Verify directories were created
        assert mock_makedirs.call_count >= 5  # One for each format

        # Verify files were written
        assert mock_file.call_count >= 5  # One for each format

class TestContentFormatterIntegration:
    """Integration tests for ContentFormatter"""

    @pytest.fixture
    def formatter(self):
        """Create real formatter instance for integration tests"""
        return ContentFormatter()

    def test_format_pipeline(self, formatter, sample_research_report, temp_dir):
        """Test complete formatting pipeline"""
        # This would be a more comprehensive integration test
        # that tests the full pipeline without mocking
        pass