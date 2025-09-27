#!/bin/bash

# Release creation script for research automation project

set -e

# Configuration
PROJECT_NAME="research-automation"
GITHUB_REPO="nicks-sidehustle/research-automation"
RELEASE_BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if we're on the right branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "$RELEASE_BRANCH" ]]; then
        log_error "Must be on $RELEASE_BRANCH branch for release. Currently on: $current_branch"
        exit 1
    fi

    # Check if working directory is clean
    if [[ -n $(git status --porcelain) ]]; then
        log_error "Working directory is not clean. Please commit or stash changes."
        exit 1
    fi

    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first."
        exit 1
    fi

    # Check if logged into GitHub
    if ! gh auth status &> /dev/null; then
        log_error "Not logged into GitHub. Please run 'gh auth login' first."
        exit 1
    fi

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed."
        exit 1
    fi

    log_info "All prerequisites met."
}

run_tests() {
    log_info "Running tests..."

    # Install test dependencies if not already installed
    if [[ ! -f ".test_deps_installed" ]]; then
        log_info "Installing test dependencies..."
        pip install pytest pytest-cov pytest-asyncio flake8 black mypy || {
            log_error "Failed to install test dependencies"
            exit 1
        }
        touch .test_deps_installed
    fi

    # Run linting
    log_info "Running code quality checks..."
    flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
        log_error "Code quality checks failed"
        exit 1
    }

    # Run tests
    log_info "Running unit tests..."
    pytest tests/unit/ -v || {
        log_error "Unit tests failed"
        exit 1
    }

    log_info "All tests passed."
}

get_version_bump_type() {
    local bump_type=""

    echo "Select version bump type:"
    echo "1) patch (bug fixes)"
    echo "2) minor (new features)"
    echo "3) major (breaking changes)"
    read -p "Enter choice (1-3): " choice

    case $choice in
        1) bump_type="patch" ;;
        2) bump_type="minor" ;;
        3) bump_type="major" ;;
        *) log_error "Invalid choice"; exit 1 ;;
    esac

    echo $bump_type
}

bump_version() {
    local bump_type=$1

    log_info "Bumping version ($bump_type)..."

    # Run the version bump script
    python3 scripts/version/bump_version.py $bump_type --auto-commit || {
        log_error "Version bump failed"
        exit 1
    }

    # Get the new version
    local new_version=$(cat VERSION 2>/dev/null || echo "unknown")
    echo $new_version
}

generate_release_notes() {
    local version=$1
    local temp_file=$(mktemp)

    log_info "Generating release notes..."

    # Get commits since last tag
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    local commit_range=""

    if [[ -n "$last_tag" ]]; then
        commit_range="$last_tag..HEAD"
    else
        commit_range="HEAD"
    fi

    # Generate changelog
    cat > $temp_file << EOF
# Release v$version

## What's Changed

EOF

    # Add commit messages (formatted)
    git log $commit_range --oneline --no-merges | while read line; do
        echo "- $line" >> $temp_file
    done

    cat >> $temp_file << EOF

## Installation

\`\`\`bash
git clone https://github.com/$GITHUB_REPO.git
cd $PROJECT_NAME
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
\`\`\`

## Usage

\`\`\`bash
# Conduct research and generate content
python src/research/research_orchestrator.py --topic "Your Topic" --content-type blog

# Export to multiple formats
python src/export/content_formatter.py --report outputs/reports/latest.json --format all
\`\`\`

## Full Changelog

View the complete changelog at: https://github.com/$GITHUB_REPO/compare/$last_tag...v$version
EOF

    echo $temp_file
}

create_github_release() {
    local version=$1
    local release_notes_file=$2

    log_info "Creating GitHub release..."

    # Push the tag
    git push origin v$version || {
        log_error "Failed to push tag"
        exit 1
    }

    # Create the release
    gh release create "v$version" \
        --title "Release v$version" \
        --notes-file "$release_notes_file" \
        --target "$RELEASE_BRANCH" || {
        log_error "Failed to create GitHub release"
        exit 1
    }

    log_info "GitHub release created successfully!"
}

cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f .test_deps_installed
    # Remove any other temporary files created during the process
}

main() {
    log_info "Starting release process for $PROJECT_NAME..."

    # Trap to ensure cleanup happens
    trap cleanup EXIT

    # Check prerequisites
    check_prerequisites

    # Run tests
    run_tests

    # Get version bump type
    bump_type=$(get_version_bump_type)

    # Confirm release
    read -p "Are you sure you want to create a $bump_type release? (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        log_info "Release cancelled."
        exit 0
    fi

    # Bump version
    new_version=$(bump_version $bump_type)

    # Generate release notes
    release_notes_file=$(generate_release_notes $new_version)

    # Show release notes for review
    log_info "Release notes:"
    cat $release_notes_file

    # Confirm release notes
    read -p "Proceed with these release notes? (y/N): " confirm_notes
    if [[ $confirm_notes != [yY] ]]; then
        log_info "Release cancelled."
        exit 0
    fi

    # Create GitHub release
    create_github_release $new_version $release_notes_file

    # Success message
    log_info "Release v$new_version created successfully!"
    log_info "View at: https://github.com/$GITHUB_REPO/releases/tag/v$new_version"

    # Clean up release notes file
    rm -f $release_notes_file
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--help]"
        echo "Creates a new release for the research automation project"
        echo ""
        echo "This script will:"
        echo "  1. Check prerequisites and run tests"
        echo "  2. Prompt for version bump type"
        echo "  3. Bump version and create git tag"
        echo "  4. Generate release notes"
        echo "  5. Create GitHub release"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown argument: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac