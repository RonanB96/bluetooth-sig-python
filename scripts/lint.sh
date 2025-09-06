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
    RUFF_OUTPUT=$(ruff check src/ tests/ examples/ 2>&1)
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

    # Run pylint and capture output, allowing it to fail
    local PYLINT_OUTPUT
    set +e  # Temporarily disable exit on error
    PYLINT_OUTPUT=$(pylint src/bluetooth_sig examples 2>&1)
    set -e  # Re-enable exit on error

    # Always show the pylint output first
    echo "$PYLINT_OUTPUT"
    echo ""

    # Extract score using sed (compatible with BusyBox)
    SCORE=$(echo "$PYLINT_OUTPUT" | sed -n 's/.*rated at \([0-9]\+\.[0-9]\+\).*/\1/p' | head -1)
    echo "Pylint score: $SCORE/10"

    # Fail if score is not exactly 10.00
    if [ "$SCORE" != "10.00" ]; then
        print_error "Pylint score must be exactly 10.00/10. Current score: $SCORE/10"
        echo "Please fix all pylint issues or add justified disable comments."
        return 1
    fi

    print_success "Perfect pylint score achieved: 10.00/10"
    return 0
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
            echo "  --pylint            Run pylint analysis (must score 10.00/10)"
            echo "  --shellcheck        Run shellcheck shell script analysis"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run all linting checks"
            echo "  $0 --ruff           # Run only ruff"
            echo "  $0 --pylint         # Run only pylint"
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