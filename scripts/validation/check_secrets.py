#!/usr/bin/env python3
"""
Secret detection script for pre-commit hooks
Checks for potential API keys, tokens, and secrets in code
"""

import re
import sys
import os
from pathlib import Path

# Patterns for common secrets
SECRET_PATTERNS = [
    # API Keys
    (r'api[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9_-]{20,}', 'API Key'),
    (r'secret[_-]?key["\s]*[:=]["\s]*[a-zA-Z0-9_-]{20,}', 'Secret Key'),

    # OpenAI
    (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key'),
    (r'sk-proj-[a-zA-Z0-9_-]{20,}', 'OpenAI Project Key'),

    # Anthropic
    (r'sk-ant-api[0-9]{2}-[a-zA-Z0-9_-]{95}', 'Anthropic API Key'),

    # Google
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),

    # GitHub
    (r'gh[pousr]_[A-Za-z0-9_]{36}', 'GitHub Token'),
    (r'github_pat_[a-zA-Z0-9_]{82}', 'GitHub Personal Access Token'),

    # Generic patterns
    (r'xai-[a-zA-Z0-9_-]{50,}', 'xAI API Key'),
    (r'Bearer [a-zA-Z0-9_.-]{20,}', 'Bearer Token'),
    (r'token["\s]*[:=]["\s]*[a-zA-Z0-9_-]{20,}', 'Generic Token'),

    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'aws_secret_access_key["\s]*[:=]["\s]*[a-zA-Z0-9+/]{40}', 'AWS Secret Key'),

    # Database URLs with passwords
    (r'[a-zA-Z][a-zA-Z0-9+.-]*://[^:]+:[^@]+@', 'Database URL with credentials'),

    # Private keys
    (r'-----BEGIN (RSA )?PRIVATE KEY-----', 'Private Key'),
    (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'SSH Private Key'),
]

# Files to exclude from secret scanning
EXCLUDED_FILES = {
    '.env.example',
    'check_secrets.py',  # This file
    'test_secrets.py',   # Test files might contain fake secrets
    'README.md',         # Documentation might show examples
    'SECURITY.md',
}

# Directories to exclude
EXCLUDED_DIRS = {
    '.git',
    'node_modules',
    '__pycache__',
    '.pytest_cache',
    'htmlcov',
    'build',
    'dist',
}

class SecretDetector:
    def __init__(self):
        self.secrets_found = []

    def is_excluded_file(self, file_path):
        """Check if file should be excluded from scanning"""
        path = Path(file_path)

        # Check filename
        if path.name in EXCLUDED_FILES:
            return True

        # Check if in excluded directory
        for part in path.parts:
            if part in EXCLUDED_DIRS:
                return True

        return False

    def scan_content(self, content, file_path):
        """Scan file content for secrets"""
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip comments and certain lines
            stripped_line = line.strip()

            # Skip obvious comments
            if stripped_line.startswith('#') or stripped_line.startswith('//'):
                continue

            # Skip lines that look like examples or documentation
            if any(word in stripped_line.lower() for word in ['example', 'placeholder', 'your_api_key', 'xxx', 'dummy']):
                continue

            # Check against patterns
            for pattern, secret_type in SECRET_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    self.secrets_found.append({
                        'file': file_path,
                        'line': line_num,
                        'type': secret_type,
                        'content': line.strip(),
                        'match': match.group()
                    })

    def scan_file(self, file_path):
        """Scan a single file for secrets"""
        if self.is_excluded_file(file_path):
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                self.scan_content(content, file_path)
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

    def scan_files(self, file_paths):
        """Scan multiple files for secrets"""
        for file_path in file_paths:
            if os.path.isfile(file_path):
                self.scan_file(file_path)

    def report_findings(self):
        """Report found secrets"""
        if not self.secrets_found:
            return True

        print("🚨 SECURITY ALERT: Potential secrets detected!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        for secret in self.secrets_found:
            print(f"File: {secret['file']}", file=sys.stderr)
            print(f"Line: {secret['line']}", file=sys.stderr)
            print(f"Type: {secret['type']}", file=sys.stderr)
            print(f"Content: {secret['content']}", file=sys.stderr)
            print(f"Match: {secret['match'][:50]}{'...' if len(secret['match']) > 50 else ''}", file=sys.stderr)
            print("-" * 40, file=sys.stderr)

        print("\n❌ Commit blocked due to potential secrets.", file=sys.stderr)
        print("Please review and remove any real secrets before committing.", file=sys.stderr)
        print("If these are false positives, add them to the exclusion list.", file=sys.stderr)

        return False

def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Scan files for potential secrets')
    parser.add_argument('files', nargs='*', help='Files to scan')
    parser.add_argument('--all', action='store_true', help='Scan all files in project')

    args = parser.parse_args()

    detector = SecretDetector()

    if args.all:
        # Scan all files in project
        project_root = Path(__file__).parent.parent.parent
        for file_path in project_root.rglob('*'):
            if file_path.is_file():
                detector.scan_file(str(file_path))
    else:
        # Scan specified files
        detector.scan_files(args.files if args.files else sys.argv[1:])

    # Report findings
    success = detector.report_findings()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()