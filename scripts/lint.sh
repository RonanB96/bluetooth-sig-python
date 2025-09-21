#!/bin/bash

set -euo pipefail

# Default to running all linting checks if no argument provided
if [ $# -eq 0 ]; then
    set -- --all
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Folders to lint/format
RUFF_FOLDERS="src/ tests/ examples/"
BLUETOOTH_SIG_FOLDERS="src/bluetooth_sig examples"
TEST_FOLDERS="tests/"

# Print functions
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check virtual environment
check_venv() {
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        print_warning "No virtual environment detected"
        print_warning "Consider running: source .venv/bin/activate"
    else
        print_success "Virtual environment active: $VIRTUAL_ENV"
    fi
    echo ""
}

# Run ruff linting (replaces flake8)
run_ruff() {
    print_header "Running ruff"

    if ! command -v ruff >/dev/null 2>&1; then
        print_error "ruff not found. Install with: pip install ruff"
        return 1
    fi

    # Run ruff and capture output, allowing it to fail
    local RUFF_OUTPUT
    set +e  # Temporarily disable exit on error
    RUFF_OUTPUT=$(ruff check $RUFF_FOLDERS 2>&1)
    local RUFF_EXIT_CODE=$?
    set -e  # Re-enable exit on error

    if [ $RUFF_EXIT_CODE -eq 0 ]; then
        print_success "ruff passed with zero violations"
        return 0
    else
        # Show the actual ruff output
        echo "$RUFF_OUTPUT"
        print_error "ruff found violations"
        return 1
    fi
}

# Run pylint
run_pylint() {
    print_header "Running pylint"

    if ! command -v pylint >/dev/null 2>&1; then
        print_error "pylint not found. Install with: pip install pylint"
        return 1
    fi

    local exit_code=0

    # Run pylint on production code (strict requirements)
    echo "Checking production code..."
    local PROD_PYLINT_OUTPUT
    set +e  # Temporarily disable exit on error
    PROD_PYLINT_OUTPUT=$(pylint $BLUETOOTH_SIG_FOLDERS 2>&1)
    set -e  # Re-enable exit on error

    # Extract production score
    PROD_SCORE=$(echo "$PROD_PYLINT_OUTPUT" | sed -n 's/.*rated at \([0-9]\+\.[0-9]\+\).*/\1/p' | head -1)
    echo "Production pylint score: $PROD_SCORE/10"

    # Production code must be perfect
    if [ "$PROD_SCORE" != "10.00" ]; then
        print_error "Production pylint score must be exactly 10.00/10. Current score: $PROD_SCORE/10"
        echo "Please fix all pylint issues in production code or add justified disable comments."
        exit_code=1
    else
        print_success "Production code achieved perfect pylint score: 10.00/10"
    fi

    echo ""

    # Run pylint on tests (more lenient requirements)
    echo "Checking test code..."
    local TEST_PYLINT_OUTPUT
    set +e  # Temporarily disable exit on error
    TEST_PYLINT_OUTPUT=$(pylint $TEST_FOLDERS 2>&1)
    set -e  # Re-enable exit on error

    # Extract test score
    TEST_SCORE=$(echo "$TEST_PYLINT_OUTPUT" | sed -n 's/.*rated at \([0-9]\+\.[0-9]\+\).*/\1/p' | head -1)
    echo "Test pylint score: $TEST_SCORE/10"

    # Tests need minimum 8.00 score (reasonable but not perfect)
    local MIN_TEST_SCORE="8.00"
    if [ "$(echo "$TEST_SCORE < $MIN_TEST_SCORE" | bc -l 2>/dev/null || echo "1")" = "1" ]; then
        print_error "Test pylint score must be at least $MIN_TEST_SCORE/10. Current score: $TEST_SCORE/10"
        echo "Please improve test code quality or add justified disable comments."
        exit_code=1
    else
        print_success "Test code achieved acceptable pylint score: $TEST_SCORE/10 (minimum: $MIN_TEST_SCORE/10)"
    fi

    # Show detailed output if there were issues
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "Production pylint output:"
        echo "$PROD_PYLINT_OUTPUT"
        echo ""
        echo "Test pylint output:"
        echo "$TEST_PYLINT_OUTPUT"
    fi

    return $exit_code
}

# Run mypy type checking
run_mypy() {
    print_header "Running mypy type checking"

    if ! command -v mypy >/dev/null 2>&1; then
        print_warning "mypy not found. Install with: pip install mypy"
        print_warning "Skipping type checking"
        return 0
    fi

    local exit_code=0

    # Run mypy on production code (strict)
    echo "Checking production code types..."
    local PROD_MYPY_OUTPUT
    set +e  # Temporarily disable exit on error
    PROD_MYPY_OUTPUT=$(mypy $BLUETOOTH_SIG_FOLDERS 2>&1)
    local PROD_MYPY_EXIT_CODE=$?
    set -e  # Re-enable exit on error

    if [ $PROD_MYPY_EXIT_CODE -eq 0 ]; then
        print_success "Production code type checking passed"
    else
        print_error "Production code type checking failed"
        echo "$PROD_MYPY_OUTPUT"
        exit_code=1
    fi

    echo ""

    # Run mypy on tests (more lenient - tests often have type issues due to mocking)
    echo "Checking test code types..."
    local TEST_MYPY_OUTPUT
    set +e  # Temporarily disable exit on error
    TEST_MYPY_OUTPUT=$(mypy $TEST_FOLDERS 2>&1)
    local TEST_MYPY_EXIT_CODE=$?
    set -e  # Re-enable exit on error

    if [ $TEST_MYPY_EXIT_CODE -eq 0 ]; then
        print_success "Test code type checking passed"
    else
        print_warning "Test code has type issues (this is common and often acceptable)"
        echo "Test mypy output (non-blocking):"
        echo "$TEST_MYPY_OUTPUT"
        # Don't set exit_code=1 for test type issues - they're often expected
    fi

    return $exit_code
}

# Run shellcheck
run_shellcheck() {
    print_header "Running shellcheck"

    if ! command -v shellcheck >/dev/null 2>&1; then
        print_error "shellcheck not found. Install with: apt-get install shellcheck or brew install shellcheck"
        return 1
    fi

    # Find all shell scripts in the project
    local shell_scripts
    shell_scripts=$(find . -name "*.sh" -type f | grep -v ".venv" | head -20)

    if [ -z "$shell_scripts" ]; then
        print_warning "No shell scripts found to check"
        return 0
    fi

    echo "Checking shell scripts:"
    echo "$shell_scripts"
    echo ""

    # Run shellcheck on all shell scripts
    local exit_code=0
    local total_issues=0

    while IFS= read -r script; do
        if [ -n "$script" ]; then
            echo "Checking: $script"

            # Run shellcheck, allowing it to fail
            set +e  # Temporarily disable exit on error
            shellcheck "$script"
            local script_exit_code=$?
            set -e  # Re-enable exit on error

            if [ $script_exit_code -ne 0 ]; then
                exit_code=1
                # Count issues for this script
                local script_issues
                script_issues=$(shellcheck "$script" 2>&1 | grep -c "^In " || true)
                total_issues=$((total_issues + script_issues))
            fi
            echo ""
        fi
    done <<< "$shell_scripts"

    if [ $exit_code -eq 0 ]; then
        print_success "shellcheck passed with zero issues"
        return 0
    else
        print_error "shellcheck found $total_issues issues"
        echo "Please fix shellcheck issues or add shellcheck disable comments where justified."
        return 1
    fi
}

# Run all linting checks
run_all_checks() {
    print_header "Running all linting checks"
    local exit_code=0

    check_venv

    if ! run_ruff; then
        exit_code=1
    fi

    echo ""

    if ! run_pylint; then
        exit_code=1
    fi

    echo ""

    if ! run_mypy; then
        exit_code=1
    fi

    echo ""

    if ! run_shellcheck; then
        exit_code=1
    fi

    echo ""

    if [ $exit_code -eq 0 ]; then
        print_success "🚀 All linting checks passed!"
    else
        print_error "💥 Some linting checks failed"
    fi

    return $exit_code
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all|--check)
            run_all_checks
            exit $?
            ;;
        --ruff)
            check_venv
            run_ruff
            exit $?
            ;;
        --pylint)
            check_venv
            run_pylint
            exit $?
            ;;
        --mypy)
            check_venv
            run_mypy
            exit $?
            ;;
        --shellcheck)
            run_shellcheck
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Code linting script for BLE GATT Device"
            echo ""
            echo "OPTIONS:"
            echo "  --all, --check      Run all linting checks (default)"
            echo ""
            echo "Individual tools:"
            echo "  --ruff              Run ruff linting (replaces flake8)"
            echo "  --pylint            Run pylint analysis (production: 10.00/10, tests: ≥8.00/10)"
            echo "  --mypy              Run mypy type checking (production: strict, tests: lenient)"
            echo "  --shellcheck        Run shellcheck shell script analysis"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run all linting checks"
            echo "  $0 --ruff           # Run only ruff"
            echo "  $0 --pylint         # Run only pylint"
            echo "  $0 --mypy           # Run only mypy"
            echo "  $0 --shellcheck     # Run only shellcheck"
            echo ""
            echo "Note: For formatting, use ./scripts/format.sh"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for available options"
            exit 1
            ;;
    esac
done

# If no options provided, run all checks
if [ $# -eq 0 ]; then
    run_all_checks
fi