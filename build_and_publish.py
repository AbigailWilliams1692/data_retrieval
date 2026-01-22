#!/usr/bin/env python3
"""
Build and publish script for Data Retrieval Module.
This script automates the process of building and publishing the package to PyPI.

Author: AbigailWilliams1692
Created: 2026-01-14
Updated: 2026-01-14
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result


def check_git_status():
    """Check if git working directory is clean."""
    print("Checking git status...")
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("❌ Working directory is not clean. Please commit or stash changes first.")
        return False
    print("✅ Git working directory is clean")
    return True


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    try:
        run_command("python -m pytest tests/ -v")
        print("✅ All tests passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        return False


def run_code_quality_checks():
    """Run code quality checks."""
    print("Running code quality checks...")
    
    # Check if required tools are installed
    tools = ["black", "isort", "mypy", "flake8"]
    for tool in tools:
        try:
            run_command(f"{tool} --version", check=False)
        except subprocess.CalledProcessError:
            print(f"❌ {tool} is not installed. Install with: pip install {tool}")
            return False
    
    # Run formatting checks
    try:
        print("Checking code formatting with black...")
        run_command("black --check data_retrieval/ tests/")
        print("✅ Black formatting check passed")
    except subprocess.CalledProcessError:
        print("❌ Code formatting issues found. Run: black data_retrieval/ tests/")
        return False
    
    try:
        print("Checking import sorting with isort...")
        run_command("isort --check-only data_retrieval/ tests/")
        print("✅ Import sorting check passed")
    except subprocess.CalledProcessError:
        print("❌ Import sorting issues found. Run: isort data_retrieval/ tests/")
        return False
    
    # Run type checking (optional, might fail on some projects)
    try:
        print("Running type checking with mypy...")
        run_command("mypy data_retrieval/", check=False)
        print("✅ Type checking passed")
    except subprocess.CalledProcessError:
        print("⚠️ Type checking failed (optional)")
    
    return True


def clean_build_artifacts():
    """Clean previous build artifacts."""
    print("Cleaning build artifacts...")
    
    # Remove build directories
    dirs_to_remove = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Removing directory: {path}")
                import shutil
                shutil.rmtree(path)
            else:
                print(f"Removing file: {path}")
                path.unlink()
    
    print("✅ Build artifacts cleaned")


def build_package():
    """Build the package using modern build system."""
    print("Building package...")
    
    # Use python -m build for modern building
    run_command("python -m build")
    
    print("✅ Package built successfully")
    return True


def check_package():
    """Check the built package with twine."""
    print("Checking package with twine...")
    
    try:
        run_command("twine check dist/*")
        print("✅ Package check passed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Package check failed")
        return False


def upload_to_test_pypi():
    """Upload package to Test PyPI."""
    print("Uploading to Test PyPI...")
    
    try:
        run_command("twine upload --repository testpypi dist/*")
        print("✅ Uploaded to Test PyPI successfully")
        print("📦 Install with: pip install --index-url https://test.pypi.org/simple/ data-retrieval-module")
        return True
    except subprocess.CalledProcessError:
        print("❌ Upload to Test PyPI failed")
        return False


def upload_to_pypi():
    """Upload package to PyPI."""
    print("Uploading to PyPI...")
    
    try:
        run_command("twine upload dist/*")
        print("✅ Uploaded to PyPI successfully")
        print("📦 Install with: pip install data-retrieval-module")
        return True
    except subprocess.CalledProcessError:
        print("❌ Upload to PyPI failed")
        return False


def main():
    """Main function."""
    print("🚀 Data Retrieval Module - Build and Publish Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists() and not Path("pyproject.toml").exists():
        print("❌ Not in a package directory (setup.py or pyproject.toml not found)")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python build_and_publish.py test      # Build and upload to Test PyPI")
        print("  python build_and_publish.py prod      # Build and upload to PyPI")
        print("  python build_and_publish.py build     # Build only")
        print("  python build_and_publish.py check     # Run checks only")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Pre-flight checks
    if not check_git_status():
        sys.exit(1)
    
    if not run_tests():
        sys.exit(1)
    
    if not run_code_quality_checks():
        print("⚠️ Code quality issues found. Continue anyway? (y/N)")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Clean and build
    clean_build_artifacts()
    
    if not build_package():
        sys.exit(1)
    
    if not check_package():
        sys.exit(1)
    
    # Upload based on command
    if command == "test":
        upload_to_test_pypi()
    elif command == "prod":
        upload_to_pypi()
    elif command == "build":
        print("✅ Build completed. Package ready in dist/ directory")
    elif command == "check":
        print("✅ All checks passed")
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
