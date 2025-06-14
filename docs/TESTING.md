# Testing Guide

This document explains the different testing approaches available in the esxport project.

## Testing Levels

### 1. Unit Tests
**Purpose:** Test individual functions and classes in isolation.

```bash
# Run unit tests
hatch run test

# Run with coverage
hatch run test-cov
hatch run cov-report
```

### 2. Integration Tests
**Purpose:** Test the built package to catch packaging issues.

```bash
# Test wheel package
hatch run integration:test-wheel

# Test source distribution
hatch run integration:test-sdist

# Test both
hatch run integration:test-both
```

### 3. Code Quality
**Purpose:** Ensure code formatting and style consistency.

```bash
# Run all quality checks
hatch run lint:style

# Format code
hatch run lint:fmt
```

## Comprehensive Testing

### Local Development - `scripts/test-all.sh`
**When to use:** Before committing, before releases, debugging issues locally.

```bash
# Run all tests locally
./scripts/test-all.sh

# Include multi-version testing
./scripts/test-all.sh --all-versions
```

**Features:**
- ✅ Colored output for easy reading
- ✅ Detailed progress tracking
- ✅ Summary of failed tests
- ✅ 5-phase testing approach
- ✅ Pre-release validation

### CI/CD - GitHub Actions
**When to use:** Automatic testing on PRs and pushes.

#### Unit Tests (pytest.yml)
- Runs on every PR and push to main
- Tests across multiple Python versions
- Includes coverage reporting
- Fast feedback for code changes

#### Integration Tests (integration-tests.yml)
- Runs on every PR and push to main
- Tests built packages (wheel/sdist)
- Package isolation testing
- Installation method validation

### For CI/CD
1. **Pull Requests:** Unit tests + Integration tests across Python versions
2. **Main branch:** Same as PRs (no duplication)
3. **Manual comprehensive testing:** Use `./scripts/test-all.sh` locally

## Testing Strategy

### For Development
1. **Quick feedback:** `hatch run test`
2. **Before commit:** `./scripts/test-all.sh`
3. **Integration check:** `hatch run integration:test-both`

### For Releases
1. **Pre-release:** `./scripts/test-all.sh --all-versions`
2. **Package validation:** `hatch run release:check`
3. **Final check:** Manual comprehensive test run

## Test Environment Matrix

| Test Type     | Local Dev | PR/Push | Manual |
|---------------|-----------|---------|--------|
| Unit Tests    | ✅         | ✅       | ✅      |
| Integration   | ✅         | ✅       | ✅      |
| Multi-Python  | Optional  | ✅       | ✅      |
| Comprehensive | ✅         | ❌       | ✅      |
| Package Build | ✅         | ✅       | ✅      |

## Quick Reference

```bash
# Daily development
hatch run test

# Before committing
./scripts/test-all.sh

# Integration testing
hatch run integration:test-both

# Code quality
hatch run lint:style

# Complete validation
./scripts/test-all.sh --all-versions
```
