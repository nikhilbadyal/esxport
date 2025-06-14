#!/bin/bash

# Comprehensive test runner for esxport
# This script runs all types of tests: unit, integration, and quality checks

set -e

echo "🚀 Running comprehensive test suite for esxport..."
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if hatch is installed
if ! command -v hatch &> /dev/null; then
    print_error "Hatch is not installed. Please install it with: pip install hatch"
    exit 1
fi

# Track test results
failed_tests=()

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"

    print_step "Running $test_name..."

    if eval "$test_command"; then
        print_success "$test_name passed"
    else
        print_error "$test_name failed"
        failed_tests+=("$test_name")
    fi
    echo
}

# 1. Code Quality Checks
print_step "Phase 1: Code Quality Checks"
echo "----------------------------"

run_test "Code Formatting Check" "hatch run lint:style"

# 2. Unit Tests
print_step "Phase 2: Unit Tests"
echo "-------------------"

run_test "Unit Tests" "hatch run test"
run_test "Unit Tests with Coverage" "hatch run test-cov"

# 3. Integration Tests
print_step "Phase 3: Integration Tests"
echo "-------------------------"

run_test "Integration Test - Wheel Package" "hatch run integration:test-wheel"
run_test "Integration Test - Source Distribution" "hatch run integration:test-sdist"

# 4. Multi-Python Version Tests (if requested)
if [[ "$1" == "--all-versions" ]]; then
    print_step "Phase 4: Multi-Version Tests"
    echo "----------------------------"

    run_test "All Python Versions" "hatch run all:test"
fi

# 5. Package Validation
print_step "Phase 5: Package Validation"
echo "---------------------------"

run_test "Build Package" "hatch build"
run_test "Package Check" "hatch run release:check"

# Summary
echo "================================================="
echo "🏁 Test Suite Summary"
echo "================================================="

if [[ ${#failed_tests[@]} -eq 0 ]]; then
    print_success "All tests passed! 🎉"
    echo
    echo "Your package is ready for:"
    echo "  • Version bumping: ./scripts/bump-version.sh <version>"
    echo "  • Manual release: hatch run release:upload"
    echo "  • Development: hatch shell"
    exit 0
else
    print_error "Some tests failed:"
    for test in "${failed_tests[@]}"; do
        echo "  • $test"
    done
    echo
    echo "Please fix the failing tests before proceeding."
    exit 1
fi
