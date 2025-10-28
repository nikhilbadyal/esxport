# Hatch Development Guide

This project uses [Hatch](https://hatch.pypa.io/) as the primary development tool for package management, environment isolation, and build automation.

## 📋 Table of Contents

- [Installation](#installation)
- [Available Environments](#available-environments)
- [Common Commands](#common-commands)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Release Management](#release-management)
- [Migration from Requirements Files](#migration-from-requirements-files)

## 🚀 Installation

### Install Hatch

```bash
# macOS/Linux
pip install hatch

# Or via pipx (recommended)
pipx install hatch

# Verify installation
hatch --version
```

### Project Setup

```bash
# Clone the repository
git clone https://github.com/nikhilbadyal/esxport.git
cd esxport

# Hatch will automatically create environments when needed
hatch env show  # View available environments
```

## 🏗️ Available Environments

### **Default Environment** (`default`)
Primary development environment with testing capabilities.

**Dependencies:**
- `coverage[toml]>=6.5` - Code coverage analysis
- `pytest>=7.0` - Testing framework
- All project dependencies from `requirements.txt`

**Usage:**
```bash
hatch shell                    # Activate environment
hatch run test                 # Run tests
hatch run test-cov            # Run tests with coverage
hatch run cov                 # Generate coverage report
```

### **Lint Environment** (`lint`)
Isolated environment for code quality tools.

**Dependencies:**
- `black>=23.1.0` - Code formatter
- `mypy>=1.0.0` - Type checker
- `ruff>=0.0.243` - Fast linter

**Usage:**
```bash
hatch run lint:style          # Check code style
hatch run lint:fmt            # Format code and fix issues
hatch run lint:typing         # Run type checking
hatch run lint:all            # Run all quality checks
```

### **Documentation Environment** (`docs`)
Environment for building and serving documentation.

**Dependencies:**
- `mkdocs>=1.4.0` - Documentation generator
- `mkdocs-material>=8.5.0` - Material theme

**Usage:**
```bash
hatch run docs:serve          # Serve docs locally (http://localhost:8000)
hatch run docs:build          # Build static documentation
```

### **Release Environment** (`release`)
Tools for version management and package publishing.

**Dependencies:**
- `tbump>=6.11.0` - Version bumping
- `twine>=4.0.0` - PyPI publishing

**Usage:**
```bash
hatch run release:bump 9.0.3  # Bump version
hatch run release:check       # Validate built packages
hatch run release:upload-test # Upload to TestPyPI
hatch run release:upload      # Upload to PyPI
```

### **Integration Environment** (`integration`)
Test built packages to catch packaging issues.

**Dependencies:**
- `pytest>=7.0` - Testing framework
- `pip>=23.0` - Package installation

**Usage:**
```bash
hatch run integration:test        # Run integration tests
hatch run integration:test-wheel  # Build wheel and test it
hatch run integration:test-sdist  # Build source dist and test it
hatch run integration:test-both   # Test both wheel and sdist
```

### **Matrix Testing** (`all`)
Test across multiple Python versions (3.10, 3.11, 3.12, 3.13).

**Usage:**
```bash
hatch run all:test           # Run tests on all Python versions
```

## 🔧 Common Commands

### **Development**
```bash
# Enter development shell
hatch shell

# Install project in development mode
hatch run pip install -e .

# Run specific command in environment
hatch run python -c "import esxport; print(esxport.__version__)"
```

### **Testing**
```bash
# Quick test run
hatch run test

# Test with coverage
hatch run test-cov

# Full coverage report
hatch run cov

# Test specific file
hatch run test test/test_esxport.py

# Test with options
hatch run test -- -v --tb=short

# Integration testing (test built packages)
hatch run integration:test-wheel  # Test wheel package
hatch run integration:test-sdist  # Test source distribution
hatch run integration:test-both   # Test both
```

### **Code Quality**
```bash
# Check code style (no changes)
hatch run lint:style

# Format code and fix issues
hatch run lint:fmt

# Type checking
hatch run lint:typing

# Run all quality checks
hatch run lint:all
```

### **Build & Package**
```bash
# Build package
hatch build

# Clean build artifacts
hatch clean

# Build specific target
hatch build --target wheel
hatch build --target sdist
```

## 📝 Development Workflow

### **Daily Development**
1. **Start development session:**
   ```bash
   hatch shell                    # Activate environment
   ```

2. **Make changes to code**

3. **Run tests:**
   ```bash
   hatch run test                 # Quick test
   hatch run test-cov            # With coverage
   ```

4. **Check code quality:**
   ```bash
   hatch run lint:fmt            # Format and fix
   hatch run lint:all            # Full quality check
   ```

5. **Before committing:**
   ```bash
   hatch run all:test                  # Test all Python versions
   hatch run integration:test-wheel    # Test built package
   ```

### **Feature Development**
1. **Create feature branch**
2. **Develop with testing:**
   ```bash
   # Run tests continuously during development
   hatch run test test/test_feature.py -v
   ```

3. **Quality assurance:**
   ```bash
   hatch run lint:all
   hatch run test-cov
   ```

4. **Documentation:**
   ```bash
   hatch run docs:serve          # Preview docs
   # Update documentation as needed
   ```

## 🧪 Testing

### **Basic Testing**
```bash
# Run all tests
hatch run test

# Run with verbose output
hatch run test -- -v

# Run specific test file
hatch run test test/test_esxport.py

# Run specific test function
hatch run test test/test_esxport.py::test_function_name
```

### **Coverage Testing**
```bash
# Run tests with coverage
hatch run test-cov

# Generate HTML coverage report
hatch run test-cov -- --cov-report=html

# Coverage with specific options
hatch run test-cov -- --cov-report=term-missing
```

### **Multi-Version Testing**
```bash
# Test on all supported Python versions
hatch run all:test

# Test specific version (if installed)
hatch -e py311 run test
```

### **Integration Testing**
Test the actual built packages to catch packaging issues:

```bash
# Test wheel package (recommended)
hatch run integration:test-wheel

# Test source distribution
hatch run integration:test-sdist

# Test both wheel and source distribution
hatch run integration:test-both

# Run integration tests on existing package
hatch run integration:test
```

**What Integration Tests Catch:**
- Missing files in built packages
- Import path problems
- Entry point issues
- Dependency resolution problems
- Version consistency issues
- CLI functionality in packaged version

**Integration Test Types:**
- **Import Tests** - Verify all modules can be imported
- **CLI Tests** - Test command-line interface works
- **API Tests** - Test Python API functionality
- **Isolation Tests** - Ensure package works without dev dependencies

## ✨ Code Quality

### **Formatting**
```bash
# Check formatting (no changes)
hatch run lint:style

# Apply formatting
hatch run lint:fmt

# Format specific files
hatch run black esxport/cli.py
```

### **Linting**
```bash
# Run ruff linter
hatch run ruff check .

# Fix auto-fixable issues
hatch run ruff check --fix .

# Check specific files
hatch run ruff check esxport/
```

### **Type Checking**
```bash
# Run mypy type checking
hatch run lint:typing

# Check specific module
hatch run mypy esxport/cli.py
```

## 📚 Documentation

### **Local Development**
```bash
# Serve docs locally with auto-reload
hatch run docs:serve

# Build static documentation
hatch run docs:build

# View built docs
open site/index.html  # macOS
```

### **Documentation Structure**
```
docs/
├── HATCH_DEVELOPMENT.md      # This file
├── VERSION_BUMP_AUTOMATION.md # Version automation
└── ...                       # Other documentation
```

## 🚀 Release Management

### **Version Bumping**
```bash
# Bump patch version (9.0.2 -> 9.0.3)
hatch run release:bump 9.0.3

# Bump minor version (9.0.2 -> 9.1.0)
hatch run release:bump 9.1.0

# Bump major version (9.0.2 -> 10.0.0)
hatch run release:bump 10.0.0
```

### **Package Validation**
```bash
# Build and check package
hatch build
hatch run release:check

# Test upload to TestPyPI
hatch run release:upload-test

# Production upload to PyPI
hatch run release:upload
```

### **Automated Release**
The project includes automation scripts:
```bash
# Use the automation script (recommended)
./scripts/bump-version.sh 9.0.3

# This will:
# - Create feature branch
# - Bump version with tbump
# - Run tests
# - Create PR
# - Auto-merge when CI passes
# - Trigger PyPI publishing
```

## 📦 Migration from Requirements Files

### **Before (Requirements Files)**
```bash
pip install -r requirements.txt
pip install -r requirements.dev.txt
python -m pytest
black .
mypy esxport/
```

### **After (Hatch)**
```bash
hatch run test        # Testing
hatch run lint:fmt    # Formatting
hatch run lint:typing # Type checking
```

### **Benefits of Hatch**
- ✅ **Isolated environments** - No dependency conflicts
- ✅ **Consistent commands** - Same commands across all systems
- ✅ **Version matrix testing** - Test multiple Python versions
- ✅ **Integrated tooling** - Build, test, lint in one tool
- ✅ **Reproducible environments** - Locked dependencies per environment
- ✅ **Simplified CI/CD** - Better integration with GitHub Actions

## 🔧 Configuration

The hatch configuration is defined in `pyproject.toml`:

```toml
[tool.hatch.envs.default]
dependencies = [
  "coverage[toml]>=6.5",
  "pytest>=7.0",
]

[tool.hatch.envs.lint]
detached = true
dependencies = [
  "black>=23.1.0",
  "mypy>=1.0.0",
  "ruff>=0.0.243",
]

# ... more environments
```

## 🐛 Troubleshooting

### **Environment Issues**
```bash
# Remove and recreate environment
hatch env remove default
hatch env create default

# Show environment information
hatch env show

# Find environment location
hatch env find default
```

### **Dependency Issues**
```bash
# Update dependencies
hatch dep show requirements
hatch dep update

# Show dependency tree
hatch dep show tree
```

### **Python Version Issues**
```bash
# Show available Python versions
hatch python show

# Install specific Python version
hatch python install 3.11

# Use specific Python version
hatch -e py311 run test
```

## 📋 Best Practices

### **Environment Management**
- Use specific environments for specific tasks
- Keep `lint` environment detached for consistency
- Regularly update dependencies

### **Testing**
- Run `hatch run test` frequently during development
- Use `hatch run all:test` before major releases
- Maintain high test coverage

### **Code Quality**
- Run `hatch run lint:fmt` before committing
- Use `hatch run lint:all` for comprehensive checks
- Configure your IDE to use hatch environments

### **Release Process**
- Use the automation script for version bumps
- Validate packages before publishing
- Test releases on TestPyPI first

---

## 🆘 Support

For issues with hatch:
- [Hatch Documentation](https://hatch.pypa.io/)
- [Project Issues](https://github.com/nikhilbadyal/esxport/issues)
- [Hatch GitHub](https://github.com/pypa/hatch)

---

**Happy coding with Hatch! 🎯**
