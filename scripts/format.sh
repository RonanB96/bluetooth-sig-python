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

# Run ruff formatting and import sorting
run_ruff() {
    if [ "${1:-}" = "--check" ]; then
        print_header "Checking ruff formatting and import sorting"
        local exit_code=0
        
        # Check formatting
        if ! ruff format --check src/ tests/; then
            print_error "ruff formatting issues found"
            echo "Run './scripts/format.sh --fix' to fix formatting"
            exit_code=1
        else
            print_success "ruff formatting check passed"
        fi
        
        # Check linting (including import sorting)
        if ! ruff check src/ tests/; then
            print_error "ruff linting issues found"
            echo "Run './scripts/format.sh --fix' to fix issues"
            exit_code=1
        else
            print_success "ruff linting check passed"
        fi
        
        return $exit_code
    else
        print_header "Formatting code with ruff"
        
        # Fix formatting
        ruff format src/ tests/
        print_success "Code formatted with ruff"
        
        # Fix linting issues (including import sorting)
        ruff check --fix src/ tests/
        print_success "Code linting issues fixed with ruff"
        
        return 0
    fi
}

# Run all format checks
run_format_check() {
    print_header "Running all formatting checks"
    local exit_code=0

    check_venv

    run_ruff --check || exit_code=1

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

    run_ruff

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
if [ $# -eq 0 ]; then
    # Default action when no arguments provided
    run_format_check
    exit $?
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --ruff)
            run_ruff --check
            exit $?
            ;;
        --ruff-check)
            run_ruff --check
            exit $?
            ;;
        --ruff-fix)
            run_ruff
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
            echo "Ruff-based tools:"
            echo "  --ruff              Check ruff formatting and linting"
            echo "  --ruff-check        Check ruff formatting and linting"
            echo "  --ruff-fix          Fix ruff formatting and linting"
            echo ""
            echo "Examples:"
            echo "  $0                  # Check all formatting"
            echo "  $0 --check          # Check all formatting"
            echo "  $0 --fix            # Fix all formatting issues"
            echo "  $0 --ruff           # Check only ruff"
            echo "  $0 --ruff-fix       # Fix only ruff issues"
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
