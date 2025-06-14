#!/bin/bash

# Version Bump Automation Script
# Usage: ./scripts/bump-version.sh <new_version>
# Example: ./scripts/bump-version.sh 9.0.2

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gh CLI is installed
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed. Please install it first."
        log_info "Install with: brew install gh (macOS) or visit https://cli.github.com/"
        exit 1
    fi

    # Check if authenticated with GitHub
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI. Please run 'gh auth login' first."
        exit 1
    fi

    # Check if tbump is installed
    if ! command -v tbump &> /dev/null; then
        log_error "tbump is not installed. Installing..."
        pip install tbump
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi

    # Check if on main branch
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        log_error "Please switch to main branch first. Current branch: $current_branch"
        exit 1
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_error "You have uncommitted changes. Please commit or stash them first."
        exit 1
    fi

    log_success "All prerequisites met"
}

create_branch() {
    local version=$1
    local branch_name="upgrade/elasticsearch-$version"

    log_info "Creating branch: $branch_name"

    # Pull latest changes
    git pull origin main

    # Create and checkout new branch
    git checkout -b "$branch_name"

    log_success "Created and switched to branch: $branch_name"
    echo "$branch_name"
}

bump_version() {
    local version=$1

    log_info "Bumping version to $version using tbump..."

    # Run tbump without pushing
    if tbump "$version" --no-push; then
        log_success "Version bumped to $version"
    else
        log_error "Failed to bump version"
        exit 1
    fi
}

push_branch() {
    local branch_name=$1

    log_info "Pushing branch to origin..."

    git push origin "$branch_name"

    log_success "Branch pushed to origin"
}

create_pr() {
    local version=$1
    local branch_name=$2

    log_info "Creating Pull Request..."

    # Create PR with GitHub CLI
    pr_url=$(gh pr create \
        --title "⬆️ Bump to $version" \
        --body "## Version Bump to $version

### Changes
- Updated package version from $(git show HEAD~1:esxport/__init__.py | grep __version__ | cut -d'"' -f2) to $version
- Updated Elasticsearch dependency to $version
- Updated test environment to use Elasticsearch $version

### Testing
- [ ] All existing tests pass
- [ ] Compatibility verified with Elasticsearch $version
- [ ] Pre-commit hooks pass

This PR was created automatically by the version bump script.

**Note:** This PR will be auto-merged once all checks pass." \
        --base main \
        --head "$branch_name")

    log_success "Pull Request created: $pr_url"
    echo "$pr_url"
}

wait_for_checks() {
    local pr_url=$1

    log_info "Waiting for CI checks to complete..."

    # Extract PR number from URL
    pr_number=$(echo "$pr_url" | grep -o '[0-9]*$')

    # Wait for checks to complete
    log_info "Monitoring PR #$pr_number for check completion..."

    while true; do
        # Get check status
        check_status=$(gh pr checks "$pr_number" --json state --jq '.[].state' | sort | uniq)

        if echo "$check_status" | grep -q "FAILURE\|ERROR"; then
            log_error "Some checks failed. Please review the PR: $pr_url"
            return 1
        elif echo "$check_status" | grep -q "PENDING\|IN_PROGRESS"; then
            log_info "Checks still running... waiting 30 seconds"
            sleep 30
        elif echo "$check_status" | grep -q "SUCCESS" && ! echo "$check_status" | grep -q "PENDING\|IN_PROGRESS"; then
            log_success "All checks passed!"
            return 0
        else
            log_warning "Unknown check status: $check_status"
            sleep 30
        fi
    done
}

merge_pr() {
    local pr_url=$1

    log_info "Auto-merging PR..."

    pr_number=$(echo "$pr_url" | grep -o '[0-9]*$')

    if gh pr merge "$pr_number" --squash --auto; then
        log_success "PR merged successfully!"
    else
        log_error "Failed to merge PR. Please merge manually: $pr_url"
        exit 1
    fi
}

cleanup() {
    log_info "Cleaning up..."

    # Switch back to main
    git checkout main

    # Pull latest changes
    git pull origin main

    # Delete local branch
    local branch_name=$1
    if [ -n "$branch_name" ] && git branch | grep -q "$branch_name"; then
        git branch -d "$branch_name"
        log_success "Deleted local branch: $branch_name"
    fi
}

main() {
    if [ $# -eq 0 ]; then
        log_error "Usage: $0 <version>"
        log_info "Example: $0 9.0.2"
        exit 1
    fi

    local version=$1
    local branch_name
    local pr_url

    log_info "Starting version bump automation for version: $version"

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Create branch
    branch_name=$(create_branch "$version")

    # Step 3: Bump version
    bump_version "$version"

    # Step 4: Push branch
    push_branch "$branch_name"

    # Step 5: Create PR
    pr_url=$(create_pr "$version" "$branch_name")

    # Step 6: Wait for checks
    if wait_for_checks "$pr_url"; then
        # Step 7: Merge PR
        merge_pr "$pr_url"

        # Step 8: Cleanup
        cleanup "$branch_name"

        log_success "🎉 Version bump to $version completed successfully!"
        log_info "The GitHub Action will automatically create a tag and publish to PyPI."
    else
        log_error "CI checks failed. Please review and fix issues manually."
        log_info "PR URL: $pr_url"
        exit 1
    fi
}

# Trap to cleanup on exit
trap 'log_warning "Script interrupted"' INT TERM

main "$@"
