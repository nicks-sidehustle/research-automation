#!/usr/bin/env python3
"""
Version bumping script for research automation project
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

class VersionBumper:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.version_file = self.project_root / "VERSION"
        self.config_file = self.project_root / "config" / "research_config.json"

    def get_current_version(self):
        """Get current version from VERSION file or default"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return "0.1.0"

    def parse_version(self, version_string):
        """Parse version string into components"""
        match = re.match(r'(\d+)\.(\d+)\.(\d+)(?:-(.+))?', version_string)
        if not match:
            raise ValueError(f"Invalid version format: {version_string}")

        major, minor, patch, prerelease = match.groups()
        return {
            'major': int(major),
            'minor': int(minor),
            'patch': int(patch),
            'prerelease': prerelease
        }

    def bump_version(self, current_version, bump_type):
        """Bump version based on type"""
        version_parts = self.parse_version(current_version)

        if bump_type == 'major':
            version_parts['major'] += 1
            version_parts['minor'] = 0
            version_parts['patch'] = 0
        elif bump_type == 'minor':
            version_parts['minor'] += 1
            version_parts['patch'] = 0
        elif bump_type == 'patch':
            version_parts['patch'] += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        # Remove prerelease for regular bumps
        version_parts['prerelease'] = None

        return self.format_version(version_parts)

    def format_version(self, version_parts):
        """Format version parts into string"""
        version = f"{version_parts['major']}.{version_parts['minor']}.{version_parts['patch']}"
        if version_parts['prerelease']:
            version += f"-{version_parts['prerelease']}"
        return version

    def update_version_file(self, new_version):
        """Update VERSION file"""
        self.version_file.write_text(new_version + '\n')
        print(f"Updated VERSION file to {new_version}")

    def update_config_version(self, new_version):
        """Update version in config files"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            config['version'] = new_version
            config['updated_at'] = datetime.now().isoformat()

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"Updated config version to {new_version}")

    def update_readme_version(self, new_version):
        """Update version references in README"""
        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            content = readme_file.read_text()

            # Update version badges or references
            # This is a simple pattern - adjust based on your README format
            content = re.sub(
                r'(version-)[\d\.]+',
                f'version-{new_version}',
                content
            )

            readme_file.write_text(content)
            print(f"Updated README version references")

    def create_changelog_entry(self, old_version, new_version, bump_type):
        """Create changelog entry"""
        changelog_file = self.project_root / "CHANGELOG.md"

        # Create changelog if it doesn't exist
        if not changelog_file.exists():
            changelog_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        else:
            changelog_content = changelog_file.read_text()

        # Add new entry
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""## [{new_version}] - {date_str}

### {bump_type.title()}
- Version bump from {old_version} to {new_version}
- See git commits for detailed changes

"""

        # Insert after the header
        lines = changelog_content.split('\n')
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith('## [') or line.startswith('# '):
                if i > 0:  # Found first release entry
                    header_end = i
                    break
            elif i > 3:  # After reasonable header length
                header_end = i
                break

        lines.insert(header_end, new_entry)
        changelog_file.write_text('\n'.join(lines))
        print(f"Added changelog entry for {new_version}")

    def run_git_commands(self, new_version):
        """Run git commands to tag release"""
        import subprocess

        try:
            # Add changed files
            subprocess.run(['git', 'add', 'VERSION', 'config/', 'README.md', 'CHANGELOG.md'],
                         cwd=self.project_root, check=True)

            # Commit changes
            subprocess.run(['git', 'commit', '-m', f'Bump version to {new_version}'],
                         cwd=self.project_root, check=True)

            # Create tag
            subprocess.run(['git', 'tag', '-a', f'v{new_version}', '-m', f'Release v{new_version}'],
                         cwd=self.project_root, check=True)

            print(f"Created git tag v{new_version}")
            print("Run 'git push && git push --tags' to publish")

        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return False

        return True

    def bump(self, bump_type, dry_run=False, auto_commit=False):
        """Main bump function"""
        current_version = self.get_current_version()
        new_version = self.bump_version(current_version, bump_type)

        print(f"Bumping version from {current_version} to {new_version}")

        if dry_run:
            print("DRY RUN - No files will be modified")
            return new_version

        # Update files
        self.update_version_file(new_version)
        self.update_config_version(new_version)
        self.update_readme_version(new_version)
        self.create_changelog_entry(current_version, new_version, bump_type)

        if auto_commit:
            self.run_git_commands(new_version)

        return new_version

def main():
    parser = argparse.ArgumentParser(description='Bump project version')
    parser.add_argument('bump_type', choices=['major', 'minor', 'patch'],
                       help='Type of version bump')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--auto-commit', action='store_true',
                       help='Automatically commit and tag changes')
    parser.add_argument('--project-root', type=str,
                       help='Path to project root directory')

    args = parser.parse_args()

    bumper = VersionBumper(args.project_root)
    try:
        new_version = bumper.bump(args.bump_type, args.dry_run, args.auto_commit)
        print(f"Version bumped to: {new_version}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()