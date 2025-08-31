#!/bin/bash

set -euo pipefail

# Default to running format check if no arguments provided
if [ $# -eq 0 ]; then
    set -- --check
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

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check if virtual environment is activated
check_venv() {
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        print_warning "Virtual environment not detected. Consider running: source .venv/bin/activate"
    else
        print_success "Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Run black formatting
run_black() {
    if [ "$1" = "--check" ]; then
        print_header "Checking black formatting"
        if python -m black --check --diff src/ tests/; then
            print_success "black formatting check passed"
            return 0
        else
            print_error "black formatting issues found"
            echo "Run './scripts/format.sh --fix' to fix formatting"
            return 1
        fi
    else
        print_header "Formatting code with black"
        python -m black src/ tests/
        print_success "Code formatted with black"
        return 0
    fi
}

# Run isort import sorting
run_isort() {
    if [ "$1" = "--check" ]; then
        print_header "Checking isort import sorting"
        if python -m isort --check-only --diff src/ tests/; then
            print_success "isort import sorting check passed"
            return 0
        else
            print_error "isort import sorting issues found"
            echo "Run './scripts/format.sh --fix' to fix import sorting"
            return 1
        fi
    else
        print_header "Sorting imports with isort"
        python -m isort src/ tests/
        print_success "Imports sorted with isort"
        return 0
    fi
}

# Run all format checks
run_format_check() {
    print_header "Running all formatting checks"
    local exit_code=0

    check_venv

    run_black --check || exit_code=1
    run_isort --check || exit_code=1

    echo ""
    if [ $exit_code -eq 0 ]; then
        print_success "🎨 All formatting checks passed!"
    else
        print_error "❌ Some formatting checks failed"
        echo ""
        echo "Quick fix command:"
        echo "  ./scripts/format.sh --fix"
    fi

    return $exit_code
}

# Run all format fixes
run_format_fix() {
    print_header "Running all formatting fixes"

    check_venv

    run_black
    run_isort

    echo ""
    print_success "🎨 All formatting fixes applied!"

    # Show what changed
    if command -v git >/dev/null 2>&1 && [ -d .git ]; then
        if [ -n "$(git status --porcelain)" ]; then
            echo ""
            echo "📝 Files that were formatted:"
            git status --porcelain
        else
            echo ""
            echo "✨ No formatting changes needed - all files were already properly formatted!"
        fi
    fi

    return 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --black)
            run_black --check
            exit $?
            ;;
        --black-check)
            run_black --check
            exit $?
            ;;
        --black-fix)
            run_black
            exit $?
            ;;
        --isort)
            run_isort --check
            exit $?
            ;;
        --isort-check)
            run_isort --check
            exit $?
            ;;
        --isort-fix)
            run_isort
            exit $?
            ;;
        --check)
            run_format_check
            exit $?
            ;;
        --fix)
            run_format_fix
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Code formatting script for BLE GATT Device"
            echo ""
            echo "OPTIONS:"
            echo "  --check             Check all formatting (default)"
            echo "  --fix               Fix all formatting issues"
            echo ""
            echo "Individual tools:"
            echo "  --black             Check black formatting"
            echo "  --black-check       Check black formatting"
            echo "  --black-fix         Fix black formatting"
            echo "  --isort             Check isort import sorting"
            echo "  --isort-check       Check isort import sorting"
            echo "  --isort-fix         Fix isort import sorting"
            echo ""
            echo "Examples:"
            echo "  $0                  # Check all formatting"
            echo "  $0 --check          # Check all formatting"
            echo "  $0 --fix            # Fix all formatting issues"
            echo "  $0 --black          # Check only black"
            echo "  $0 --isort-fix      # Fix only import sorting"
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
