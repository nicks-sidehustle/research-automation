"""
End-to-end smoke tests for research automation system
"""

import pytest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

@pytest.mark.e2e
@pytest.mark.smoke
class TestSmokeTests:
    """Smoke tests to verify basic system functionality"""

    def test_import_core_modules(self):
        """Test that core modules can be imported"""
        try:
            from research.research_orchestrator import ResearchOrchestrator, ResearchQuery
            from export.content_formatter import ContentFormatter
        except ImportError as e:
            pytest.fail(f"Failed to import core modules: {e}")

    def test_create_research_query(self):
        """Test creating a research query object"""
        from research.research_orchestrator import ResearchQuery

        query = ResearchQuery(
            topic="Smoke Test Topic",
            focus_areas=["test"],
            content_type="blog",
            depth="shallow",
            target_audience="general"
        )

        assert query.topic == "Smoke Test Topic"
        assert query.content_type == "blog"
        assert query.depth == "shallow"

    def test_orchestrator_initialization(self):
        """Test that orchestrator can be initialized"""
        from research.research_orchestrator import ResearchOrchestrator

        # This should work even without API key for basic initialization
        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OPENAI_API_KEY", "dummy-key")
            orchestrator = ResearchOrchestrator()
            assert orchestrator is not None

    def test_content_formatter_initialization(self):
        """Test that content formatter can be initialized"""
        from export.content_formatter import ContentFormatter

        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OPENAI_API_KEY", "dummy-key")
            formatter = ContentFormatter()
            assert formatter is not None

    def test_config_file_loading(self):
        """Test configuration file can be loaded"""
        config_path = Path(__file__).parent.parent.parent / "config" / "research_config.json"

        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            assert isinstance(config, dict)
            assert "research_settings" in config
        else:
            pytest.skip("Config file not found - expected in development")

    def test_template_files_exist(self):
        """Test that template files exist and are readable"""
        templates_dir = Path(__file__).parent.parent.parent / "templates"

        expected_templates = [
            "blog/article_template.md",
            "podcast/script_template.md"
        ]

        for template_path in expected_templates:
            full_path = templates_dir / template_path
            if full_path.exists():
                # Try to read the template
                content = full_path.read_text()
                assert len(content) > 0
                assert "{{" in content  # Should contain template variables
            else:
                pytest.skip(f"Template {template_path} not found - expected in development")

    def test_output_directories_creation(self):
        """Test that output directories can be created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test creating output structure
            output_dirs = [
                "reports",
                "summaries",
                "blog",
                "podcast",
                "video",
                "ebook",
                "social"
            ]

            for dir_name in output_dirs:
                dir_path = Path(temp_dir) / dir_name
                dir_path.mkdir(exist_ok=True)
                assert dir_path.exists()
                assert dir_path.is_dir()

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and is readable"""
        req_path = Path(__file__).parent.parent.parent / "requirements.txt"

        if req_path.exists():
            content = req_path.read_text()
            assert "openai" in content
            assert len(content.strip()) > 0
        else:
            pytest.fail("requirements.txt not found")

    def test_gitignore_exists(self):
        """Test that .gitignore exists"""
        gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"

        if gitignore_path.exists():
            content = gitignore_path.read_text()
            assert ".env" in content
            assert "__pycache__" in content
        else:
            pytest.skip(".gitignore not found - expected in development")

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.api
class TestAPIConnectivitySmoke:
    """Smoke tests for API connectivity (requires real API keys)"""

    def test_openai_api_connectivity(self):
        """Test basic OpenAI API connectivity"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'dummy-key':
            pytest.skip("No valid OpenAI API key provided")

        try:
            import openai
            client = openai.OpenAI(api_key=api_key)

            # Simple API test
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheaper model for testing
                messages=[{"role": "user", "content": "Say 'API test successful'"}],
                max_tokens=10
            )

            assert response.choices[0].message.content is not None
        except Exception as e:
            pytest.fail(f"OpenAI API connectivity test failed: {e}")

@pytest.mark.e2e
@pytest.mark.smoke
class TestBasicWorkflow:
    """Test basic workflow without real API calls"""

    def test_research_query_to_report_structure(self):
        """Test that research query generates expected report structure"""
        from research.research_orchestrator import ResearchOrchestrator, ResearchQuery

        query = ResearchQuery(
            topic="Test Workflow",
            focus_areas=["test"],
            content_type="blog",
            depth="shallow",
            target_audience="general"
        )

        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OPENAI_API_KEY", "dummy-key")
            orchestrator = ResearchOrchestrator()

            # Test report structure creation (without AI calls)
            synthesis = {
                "executive_summary": "Test summary",
                "key_themes": ["Theme 1"],
                "supporting_evidence": ["Evidence 1"],
                "content_recommendations": {},
                "actionable_insights": ["Insight 1"]
            }

            # This should work without API calls
            import asyncio
            report = asyncio.run(orchestrator.generate_report(synthesis, query))

            # Verify report structure
            assert isinstance(report, dict)
            assert "metadata" in report
            assert "executive_summary" in report
            assert "export_formats" in report
            assert report["metadata"]["topic"] == query.topic

    def test_content_formatting_structure(self):
        """Test content formatting produces expected structure"""
        from export.content_formatter import ContentFormatter

        sample_report = {
            "metadata": {
                "topic": "Test Topic",
                "content_type": "blog",
                "target_audience": "general"
            },
            "executive_summary": "Test summary",
            "key_findings": ["Finding 1", "Finding 2"]
        }

        with pytest.MonkeyPatch().context() as mp:
            mp.setenv("OPENAI_API_KEY", "dummy-key")
            formatter = ContentFormatter()

            # Test that formatter can load report structure
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(sample_report, f)
                temp_path = f.name

            try:
                loaded_report = formatter.load_research_report(temp_path)
                assert loaded_report == sample_report
            finally:
                os.unlink(temp_path)

@pytest.mark.e2e
@pytest.mark.smoke
class TestSystemIntegration:
    """Test system-level integration points"""

    def test_version_script_exists(self):
        """Test that version management scripts exist"""
        version_script = Path(__file__).parent.parent.parent / "scripts" / "version" / "bump_version.py"

        if version_script.exists():
            # Test that it's executable Python
            content = version_script.read_text()
            assert "def main(" in content or "if __name__ == '__main__'" in content
        else:
            pytest.skip("Version script not found - expected in development")

    def test_ci_config_exists(self):
        """Test that CI configuration exists"""
        ci_config = Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml"

        if ci_config.exists():
            content = ci_config.read_text()
            assert "pytest" in content
            assert "python" in content.lower()
        else:
            pytest.skip("CI config not found - expected in development")

    def test_project_structure(self):
        """Test basic project structure"""
        project_root = Path(__file__).parent.parent.parent

        expected_dirs = [
            "src",
            "tests",
            "config",
            "templates"
        ]

        for dir_name in expected_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Expected directory {dir_name} not found"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"