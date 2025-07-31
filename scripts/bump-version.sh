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

    # Set default repository
    log_info "Setting default GitHub repository..."
    gh repo set-default --view &> /dev/null || gh repo set-default

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

    # Check for uncommitted changes more reliably
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_error "You have uncommitted changes. Here's what's changed:\n"

        echo -e "${YELLOW}--- git status ---${NC}"
        git status

        echo -e "\n${YELLOW}--- git diff (unstaged changes) ---${NC}"
        git diff

        echo -e "\n${YELLOW}--- git diff --cached (staged changes) ---${NC}"
        git diff --cached

        echo -e "\n${YELLOW}--- git diff-index HEAD (raw index diff) ---${NC}"
        git diff-index HEAD

        echo -e "\n${YELLOW}--- git diff-index HEAD --name-status ---${NC}"
        git diff-index --name-status HEAD

        echo -e "\n${RED}Please commit or stash the above changes before running the script.${NC}"
        exit 1
    fi


    log_success "All prerequisites met"
}

create_branch() {
    local version=$1
    local branch_name="upgrade/elasticsearch-$version"

    log_info "Creating branch: $branch_name"

    # Check if branch already exists and delete it
    if git branch | grep -q "$branch_name"; then
        log_warning "Branch $branch_name already exists. Deleting it..."
        git branch -D "$branch_name"
    fi

    # Check if remote branch exists and delete it
    if git ls-remote --heads origin "$branch_name" | grep -q "$branch_name"; then
        log_warning "Remote branch $branch_name exists. Deleting it..."
        git push origin --delete "$branch_name"
    fi

    # Pull latest changes
    if ! git pull origin main; then
        log_error "Failed to pull latest changes from main"
        exit 1
    fi

    # Create and checkout new branch
    if ! git checkout -b "$branch_name"; then
        log_error "Failed to create branch $branch_name"
        exit 1
    fi

    log_success "Created and switched to branch: $branch_name"
    # Return branch name without any colored output
    printf "%s" "$branch_name"
}

bump_version() {
    local version=$1

    log_info "Bumping version to $version using tbump..."

    # Run tbump without pushing and non-interactive
    if tbump "$version" --no-push --non-interactive; then
        log_success "Version bumped to $version"
    else
        log_error "Failed to bump version"
        exit 1
    fi
}

push_branch() {
    local branch_name=$1

    log_info "Pushing branch to origin..."

    if ! git push origin "$branch_name"; then
        log_error "Failed to push branch $branch_name to origin"
        exit 1
    fi

    log_success "Branch pushed to origin"
}

create_pr() {
    local version=$1
    local branch_name=$2

    log_info "Creating Pull Request..."

    # Create PR with GitHub CLI
    pr_url=$(gh pr create \
        --title "⬆️ Bump to $version" \
        --body "Version bump to Elasticsearch $version - Updates package version and dependencies" \
        --base main \
        --head "$branch_name" 2>/dev/null)

    if [ -n "$pr_url" ]; then
        log_success "Pull Request created: $pr_url"
        # Return URL without any colored output
        echo "$pr_url"
    else
        log_error "Failed to create Pull Request"
        exit 1
    fi
}

wait_for_checks() {
    local pr_url=$1

    log_info "Waiting for CI checks to complete..."

    # Extract PR number from URL
    pr_number=$(echo "$pr_url" | grep -o '[0-9]*$')

    log_info "Monitoring PR #$pr_number for check completion..."

    # First, check if any checks exist yet
    local max_wait=300  # Wait up to 5 minutes for checks to appear
    local waited=0
    while [ $waited -lt $max_wait ]; do
        if gh pr checks "$pr_number" --json state >/dev/null 2>&1; then
            break
        fi
        log_info "No checks detected yet, waiting 30 seconds... (${waited}s elapsed)"
        sleep 30
        waited=$((waited + 30))
    done

    # If still no checks after waiting, that might be normal for some repos
    if ! gh pr checks "$pr_number" --json state >/dev/null 2>&1; then
        log_warning "No CI checks detected after ${max_wait}s. Repository might not have required checks."
        log_info "Please manually verify the PR: $pr_url"
        return 0  # Assume success if no checks are configured
    fi

    # Use gh pr checks --watch with custom interval
    # This will automatically watch until checks complete
    if gh pr checks "$pr_number" --watch --interval 30; then
        log_success "All checks passed!"
        return 0
    else
        local exit_code=$?
        case $exit_code in
            8)
                log_warning "Checks are still pending. This shouldn't happen with --watch."
                log_info "Please check the PR manually: $pr_url"
                return 1
                ;;
            *)
                log_error "Some checks failed or encountered an error."
                log_info "Please review the PR: $pr_url"
                return 1
                ;;
        esac
    fi
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
        git branch -D "$branch_name"
        log_success "Deleted local branch: $branch_name"
    fi
}

validate_version() {
    local version=$1

    # Simple validation: check if version contains at least two dots and starts with number
    if [[ ! "$version" =~ ^[0-9] ]] || [[ ! "$version" =~ \. ]]; then
        log_error "Invalid version format: $version"
        log_info "Version should follow semantic versioning (e.g., 9.0.2, 9.1.0rc1)"
        exit 1
    fi

    # Count dots - should have at least 2 for major.minor.patch
    dot_count=$(echo "$version" | tr -cd '.' | wc -c)
    if [ "$dot_count" -lt 2 ]; then
        log_error "Invalid version format: $version"
        log_info "Version should have at least major.minor.patch format"
        exit 1
    fi

    log_info "Version format validated: $version"
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

    # Validate version format
    validate_version "$version"

    log_info "Starting version bump automation for version: $version"

    # Step 1: Check prerequisites
    check_prerequisites

    # Step 2: Create branch
    create_branch "$version"

    branch_name=$(git rev-parse --abbrev-ref HEAD)

    bump_version "$version"

    # Step 4: Push branch
    push_branch "$branch_name"

    # Step 5: Create PR
    pr_url=$(create_pr "$version" "$branch_name")

    # Step 6: Wait for GitHub Actions to start (they need time to trigger)
    log_info "Waiting for GitHub Actions to start..."
    sleep 60  # Give GitHub 60 seconds to start the workflows

    # Step 7: Wait for checks
    if wait_for_checks "$pr_url"; then
        # Step 8: Merge PR
        merge_pr "$pr_url"

        # Step 9: Cleanup
        cleanup "$branch_name"

        log_success "🎉 Version bump to $version completed successfully!"
        log_info "The GitHub Action will automatically create a tag and publish to PyPI."
    else
        log_error "CI checks failed. Please review and fix issues manually."
        log_info "PR URL: $pr_url"
        exit 1
    fi


}

# Cleanup function for trap
cleanup_on_exit() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_warning "Script interrupted or failed (exit code: $exit_code)"
        current_branch=$(git branch --show-current 2>/dev/null || echo "")
        if [[ "$current_branch" == upgrade/elasticsearch-* ]]; then
            log_info "Cleaning up branch: $current_branch"
            git checkout main 2>/dev/null || true
            git branch -D "$current_branch" 2>/dev/null || true
        fi
    fi
}

# Trap to cleanup on exit
trap cleanup_on_exit INT TERM EXIT

main "$@"
