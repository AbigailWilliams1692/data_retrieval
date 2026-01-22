# Publishing Guide

This guide explains how to publish the Data Retrieval Module to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at [PyPI](https://pypi.org/)
2. **API Token**: Generate an API token in your PyPI account settings
3. **Test PyPI Account**: (Optional) Create account at [Test PyPI](https://test.pypi.org/)

## Setup

### Install Required Tools

```bash
pip install build twine
```

### Configure PyPI Credentials (Optional)

Create `~/.pypirc` file:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-pypi-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-test-pypi-api-token
```

## Publishing Process

### Option 1: Using the Build Script (Recommended)

```bash
# Test publishing to Test PyPI
python build_and_publish.py test

# Production publishing to PyPI
python build_and_publish.py prod

# Build only (no upload)
python build_and_publish.py build

# Run checks only
python build_and_publish.py check
```

### Option 2: Manual Process

#### Step 1: Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info/
```

#### Step 2: Run Tests and Quality Checks

```bash
# Run tests
python -m pytest tests/ -v

# Check formatting
black --check data_retrieval tests/

# Check imports
isort --check-only data_retrieval tests/

# Type checking
mypy data_retrieval/

# Linting
flake8 data_retrieval tests/
```

#### Step 3: Build Package

```bash
python -m build
```

#### Step 4: Check Package

```bash
twine check dist/*
```

#### Step 5: Upload to Test PyPI (Optional)

```bash
twine upload --repository testpypi dist/*
```

#### Step 6: Install from Test PyPI and Test

```bash
pip install --index-url https://test.pypi.org/simple/ data-retrieval-module
```

#### Step 7: Upload to Production PyPI

```bash
twine upload dist/*
```

## Version Management

### Update Version Number

1. Update version in `pyproject.toml`:
   ```toml
   version = "1.0.1"
   ```

2. Update version in `setup.py`:
   ```python
   version="1.0.1",
   ```

3. Update `CHANGELOG.md`

4. Commit changes:
   ```bash
   git add .
   git commit -m "Bump version to 1.0.1"
   git tag v1.0.1
   git push origin main --tags
   ```

### Semantic Versioning

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Automated Publishing (GitHub Actions)

The project includes a GitHub Actions workflow that automatically:

1. Runs tests on all Python versions and platforms
2. Performs code quality checks
3. Builds the package
4. Publishes to PyPI when a release is created

### To Publish via GitHub Actions

1. Create a release on GitHub
2. Add PyPI API token to repository secrets (`PYPI_API_TOKEN`)
3. The workflow will automatically publish to PyPI

## Post-Publishing Checklist

- [ ] Verify package appears on PyPI
- [ ] Test installation from PyPI
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)
- [ ] Monitor for issues

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check `setup.py` and `pyproject.toml` syntax
   - Verify all dependencies are listed correctly

2. **Upload Failures**:
   - Check PyPI credentials
   - Verify package name is available
   - Check version number conflicts

3. **Test Installation Failures**:
   - Verify `MANIFEST.in` includes all necessary files
   - Check package structure
   - Test in clean virtual environment

### Useful Commands

```bash
# Check what files will be included
python setup.py sdist --dry-run

# List files in built package
tar -tzf dist/data-retrieval-module-1.0.0.tar.gz

# Install from local build
pip install dist/data_retrieval-module-1.0.0-py3-none-any.whl

# Uninstall package
pip uninstall data-retrieval-module
```

## Security Considerations

- Never commit API tokens to repository
- Use environment variables or GitHub secrets
- Review package contents before publishing
- Keep dependencies up to date
- Use `safety` to check for known vulnerabilities

## Support

If you encounter issues during publishing:

1. Check [PyPI documentation](https://packaging.python.org/)
2. Review [GitHub Actions logs](https://github.com/AbigailWilliams1692/data-retrieval-module/actions)
3. Open an issue on the repository

---

**Remember**: Always test on Test PyPI before publishing to production PyPI!
