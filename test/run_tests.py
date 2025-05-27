#!/usr/bin/env python3
"""
Test runner script with various test execution options
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def setup_test_environment():
    """Set up required environment variables for testing"""
    os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
    os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only_12345678901234567890")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("INIT_DB", "false")
    
    print("Test environment variables set:")
    print(f"  DATABASE_URL: {os.environ['DATABASE_URL']}")
    print(f"  SECRET_KEY: {os.environ['SECRET_KEY'][:20]}...")
    print(f"  DEBUG: {os.environ['DEBUG']}")
    print(f"  INIT_DB: {os.environ['INIT_DB']}")

def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "-m", "unit"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
    
    return run_command(cmd, "Unit Tests")

def run_integration_tests(verbose=False):
    """Run integration tests"""
    cmd = ["python", "-m", "pytest", "-m", "integration"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Integration Tests")

def run_performance_tests(verbose=False):
    """Run performance tests"""
    cmd = ["python", "-m", "pytest", "-m", "slow"]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, "Performance Tests")

def run_all_tests(verbose=False, coverage=False, skip_slow=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest"]
    
    if skip_slow:
        cmd.extend(["-m", "not slow"])
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    
    return run_command(cmd, "All Tests")

def run_specific_tests(test_path, verbose=False):
    """Run specific test file or function"""
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Specific Tests: {test_path}")

def run_tests_by_keyword(keyword, verbose=False):
    """Run tests matching keyword"""
    cmd = ["python", "-m", "pytest", "-k", keyword]
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd, f"Tests matching keyword: {keyword}")

def run_linting():
    """Run code linting"""
    commands = [
        (["python", "-m", "flake8", "app", "tests"], "Flake8 Linting"),
        (["python", "-m", "black", "--check", "app", "tests"], "Black Formatting Check"),
        (["python", "-m", "isort", "--check-only", "app", "tests"], "Import Sorting Check"),
    ]
    
    results = []
    for cmd, description in commands:
        try:
            result = run_command(cmd, description)
            results.append(result)
        except FileNotFoundError:
            print(f"WARNING: {cmd[2]} not installed, skipping {description}")
            results.append(True)  # Don't fail if tool not installed
    
    return all(results)

def generate_coverage_report():
    """Generate detailed coverage report"""
    cmd = ["python", "-m", "pytest", "--cov=app", "--cov-report=html", "--cov-report=xml"]
    
    success = run_command(cmd, "Generate Coverage Report")
    
    if success:
        print("\nCoverage reports generated:")
        print("  HTML: htmlcov/index.html")
        print("  XML: coverage.xml")
    
    return success

def clean_test_artifacts():
    """Clean up test artifacts"""
    artifacts = [
        "test.db",
        ".coverage",
        "htmlcov",
        ".pytest_cache",
        "__pycache__",
        "coverage.xml"
    ]
    
    print("Cleaning test artifacts...")
    for artifact in artifacts:
        artifact_path = Path(artifact)
        if artifact_path.exists():
            if artifact_path.is_file():
                artifact_path.unlink()
                print(f"  Removed file: {artifact}")
            elif artifact_path.is_dir():
                import shutil
                shutil.rmtree(artifact_path)
                print(f"  Removed directory: {artifact}")

def main():
    parser = argparse.ArgumentParser(description="Test runner for FastAPI English Learning App")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow/performance tests")
    parser.add_argument("--clean", action="store_true", help="Clean test artifacts before running")
    
    # Test type selection
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--unit", action="store_true", help="Run unit tests only")
    test_group.add_argument("--integration", action="store_true", help="Run integration tests only")
    test_group.add_argument("--performance", action="store_true", help="Run performance tests only")
    test_group.add_argument("--all", action="store_true", help="Run all tests (default)")
    test_group.add_argument("--file", type=str, help="Run specific test file")
    test_group.add_argument("--keyword", "-k", type=str, help="Run tests matching keyword")
    test_group.add_argument("--lint", action="store_true", help="Run linting checks")
    test_group.add_argument("--coverage-only", action="store_true", help="Generate coverage report only")
    
    args = parser.parse_args()
    
    # Setup test environment
    setup_test_environment()
    
    # Clean artifacts if requested
    if args.clean:
        clean_test_artifacts()
    
    success = True
    
    # Run appropriate tests
    if args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.performance:
        success = run_performance_tests(args.verbose)
    elif args.file:
        success = run_specific_tests(args.file, args.verbose)
    elif args.keyword:
        success = run_tests_by_keyword(args.keyword, args.verbose)
    elif args.lint:
        success = run_linting()
    elif args.coverage_only:
        success = generate_coverage_report()
    else:
        # Default: run all tests
        success = run_all_tests(args.verbose, args.coverage, args.skip_slow)
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()