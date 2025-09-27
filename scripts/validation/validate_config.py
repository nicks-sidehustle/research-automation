#!/usr/bin/env python3
"""
Configuration validation script
Validates configuration files for correctness and completeness
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_research_config(self, config: Dict[str, Any], file_path: str):
        """Validate research configuration file"""
        required_sections = [
            'research_settings',
            'content_types',
            'ai_models'
        ]

        # Check required sections
        for section in required_sections:
            if section not in config:
                self.errors.append(f"{file_path}: Missing required section '{section}'")

        # Validate research_settings
        if 'research_settings' in config:
            self.validate_research_settings(config['research_settings'], file_path)

        # Validate content_types
        if 'content_types' in config:
            self.validate_content_types(config['content_types'], file_path)

        # Validate ai_models
        if 'ai_models' in config:
            self.validate_ai_models(config['ai_models'], file_path)

    def validate_research_settings(self, settings: Dict[str, Any], file_path: str):
        """Validate research settings section"""
        required_fields = [
            'default_depth',
            'max_sources_per_query'
        ]

        for field in required_fields:
            if field not in settings:
                self.errors.append(f"{file_path}: Missing required field 'research_settings.{field}'")

        # Validate depth values
        if 'default_depth' in settings:
            valid_depths = ['shallow', 'medium', 'deep']
            if settings['default_depth'] not in valid_depths:
                self.errors.append(f"{file_path}: Invalid default_depth. Must be one of: {valid_depths}")

        # Validate numeric fields
        numeric_fields = {
            'max_sources_per_query': (1, 50),
            'research_timeout_minutes': (1, 120)
        }

        for field, (min_val, max_val) in numeric_fields.items():
            if field in settings:
                value = settings[field]
                if not isinstance(value, int) or value < min_val or value > max_val:
                    self.errors.append(f"{file_path}: {field} must be an integer between {min_val} and {max_val}")

    def validate_content_types(self, content_types: Dict[str, Any], file_path: str):
        """Validate content types section"""
        valid_content_types = ['blog', 'podcast', 'video', 'ebook']

        for content_type in content_types:
            if content_type not in valid_content_types:
                self.warnings.append(f"{file_path}: Unknown content type '{content_type}'. Valid types: {valid_content_types}")

            # Validate each content type configuration
            config = content_types[content_type]
            if not isinstance(config, dict):
                self.errors.append(f"{file_path}: Content type '{content_type}' must be an object")
                continue

            # Validate specific fields for each type
            self.validate_content_type_config(content_type, config, file_path)

    def validate_content_type_config(self, content_type: str, config: Dict[str, Any], file_path: str):
        """Validate configuration for a specific content type"""
        if content_type == 'blog':
            self.validate_blog_config(config, file_path)
        elif content_type == 'podcast':
            self.validate_podcast_config(config, file_path)
        elif content_type == 'video':
            self.validate_video_config(config, file_path)
        elif content_type == 'ebook':
            self.validate_ebook_config(config, file_path)

    def validate_blog_config(self, config: Dict[str, Any], file_path: str):
        """Validate blog configuration"""
        if 'word_count_range' in config:
            word_range = config['word_count_range']
            if not isinstance(word_range, list) or len(word_range) != 2:
                self.errors.append(f"{file_path}: blog.word_count_range must be a list of two integers")
            elif word_range[0] >= word_range[1]:
                self.errors.append(f"{file_path}: blog.word_count_range minimum must be less than maximum")

        valid_tones = ['informative', 'conversational', 'professional', 'academic', 'casual']
        if 'tone' in config and config['tone'] not in valid_tones:
            self.warnings.append(f"{file_path}: blog.tone '{config['tone']}' not in recommended list: {valid_tones}")

    def validate_podcast_config(self, config: Dict[str, Any], file_path: str):
        """Validate podcast configuration"""
        if 'duration_minutes' in config:
            duration = config['duration_minutes']
            if not isinstance(duration, list) or len(duration) != 2:
                self.errors.append(f"{file_path}: podcast.duration_minutes must be a list of two integers")
            elif duration[0] >= duration[1]:
                self.errors.append(f"{file_path}: podcast.duration_minutes minimum must be less than maximum")

    def validate_video_config(self, config: Dict[str, Any], file_path: str):
        """Validate video configuration"""
        if 'duration_seconds' in config:
            duration = config['duration_seconds']
            if not isinstance(duration, list) or len(duration) != 2:
                self.errors.append(f"{file_path}: video.duration_seconds must be a list of two integers")

        valid_platforms = ['youtube', 'tiktok', 'instagram', 'twitter', 'linkedin']
        if 'platform_optimization' in config and config['platform_optimization'] not in valid_platforms:
            self.warnings.append(f"{file_path}: video.platform_optimization '{config['platform_optimization']}' not in supported list: {valid_platforms}")

    def validate_ebook_config(self, config: Dict[str, Any], file_path: str):
        """Validate ebook configuration"""
        if 'word_count_per_chapter' in config:
            word_count = config['word_count_per_chapter']
            if not isinstance(word_count, list) or len(word_count) != 2:
                self.errors.append(f"{file_path}: ebook.word_count_per_chapter must be a list of two integers")

        valid_citation_styles = ['APA', 'MLA', 'Chicago', 'Harvard']
        if 'citation_style' in config and config['citation_style'] not in valid_citation_styles:
            self.errors.append(f"{file_path}: ebook.citation_style must be one of: {valid_citation_styles}")

    def validate_ai_models(self, models: Dict[str, Any], file_path: str):
        """Validate AI models section"""
        required_fields = [
            'research_model',
            'content_generation_model'
        ]

        for field in required_fields:
            if field not in models:
                self.errors.append(f"{file_path}: Missing required field 'ai_models.{field}'")

        # Validate model names
        valid_models = [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo',
            'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022',
            'gemini-2.0-flash-exp', 'gemini-1.5-pro'
        ]

        model_fields = ['research_model', 'content_generation_model', 'fact_checking_model']
        for field in model_fields:
            if field in models:
                model = models[field]
                if model not in valid_models:
                    self.warnings.append(f"{file_path}: ai_models.{field} '{model}' not in known models list")

        # Validate temperature values
        temperature_fields = ['temperature_research', 'temperature_content']
        for field in temperature_fields:
            if field in models:
                temp = models[field]
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    self.errors.append(f"{file_path}: ai_models.{field} must be a number between 0 and 2")

    def validate_file(self, file_path: str):
        """Validate a single configuration file"""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"{file_path}: Invalid JSON - {e}")
            return
        except IOError as e:
            self.errors.append(f"{file_path}: Cannot read file - {e}")
            return

        # Determine validation based on filename
        filename = Path(file_path).name

        if filename == 'research_config.json':
            self.validate_research_config(config, file_path)
        else:
            # Generic JSON validation for other config files
            self.validate_generic_config(config, file_path)

    def validate_generic_config(self, config: Dict[str, Any], file_path: str):
        """Basic validation for generic configuration files"""
        if not isinstance(config, dict):
            self.errors.append(f"{file_path}: Configuration must be a JSON object")

        # Check for common issues
        if len(config) == 0:
            self.warnings.append(f"{file_path}: Configuration file is empty")

    def report_results(self):
        """Report validation results"""
        success = len(self.errors) == 0

        if self.errors:
            print("❌ Configuration validation errors:", file=sys.stderr)
            for error in self.errors:
                print(f"  • {error}", file=sys.stderr)

        if self.warnings:
            print("⚠️  Configuration warnings:", file=sys.stderr)
            for warning in self.warnings:
                print(f"  • {warning}", file=sys.stderr)

        if success and not self.warnings:
            print("✅ Configuration validation passed")
        elif success:
            print("✅ Configuration validation passed (with warnings)")

        return success

def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate configuration files')
    parser.add_argument('files', nargs='*', help='Configuration files to validate')
    parser.add_argument('--config-dir', type=str, help='Directory containing config files')

    args = parser.parse_args()

    validator = ConfigValidator()

    # Determine files to validate
    files_to_validate = []

    if args.config_dir:
        config_dir = Path(args.config_dir)
        if config_dir.exists():
            files_to_validate.extend(config_dir.glob('*.json'))

    if args.files:
        files_to_validate.extend(args.files)

    if not files_to_validate:
        # Default: validate config directory
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / 'config'
        if config_dir.exists():
            files_to_validate.extend(config_dir.glob('*.json'))

    if not files_to_validate:
        print("No configuration files found to validate", file=sys.stderr)
        sys.exit(1)

    # Validate each file
    for file_path in files_to_validate:
        validator.validate_file(str(file_path))

    # Report results
    success = validator.report_results()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()