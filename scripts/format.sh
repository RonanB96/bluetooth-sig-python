#!/bin/bash

set -euo pipefail

# Default to running format check if no arguments provided
if [ $# -eq 0 ]; then
    set -- --check
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Allow overriding the project root with an explicit path
if [ -n "${PROJECT_ROOT_OVERRIDE:-}" ]; then
    if [ -d "$PROJECT_ROOT_OVERRIDE" ]; then
        PROJECT_ROOT="$(cd "$PROJECT_ROOT_OVERRIDE" && pwd)"
    else
        print_error "Provided path does not exist: $PROJECT_ROOT_OVERRIDE"
        exit 1
    fi
fi

# Change to project root
cd "$PROJECT_ROOT"

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Folders to format
RUFF_FOLDERS="src/ tests/ examples/"

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
        print_warning "Virtual environment not detected."
        if [ -n "${PROJECT_ROOT:-}" ]; then
            print_warning "Consider running: source $PROJECT_ROOT/.venv/bin/activate"
        else
            print_warning "Consider running: source .venv/bin/activate"
        fi
    else
        print_success "Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Run ruff formatting and import sorting
run_ruff() {
    local unsafe_flag=""
    if [ "${2:-}" = "--unsafe" ]; then
        unsafe_flag="--unsafe-fixes"
    fi

    if [ "${1:-}" = "--check" ]; then
        print_header "Checking ruff formatting and import sorting"
        local exit_code=0

        # Check formatting
        # shellcheck disable=SC2086  # RUFF_FOLDERS is intentionally space-separated
        if ! ruff format --check $RUFF_FOLDERS; then
            print_error "ruff formatting issues found"
            echo "Run './scripts/format.sh --fix' to fix formatting"
            exit_code=1
        else
            print_success "ruff formatting check passed"
        fi

        # Check linting (including import sorting)
        # shellcheck disable=SC2086  # RUFF_FOLDERS is intentionally space-separated
        if ! ruff check $RUFF_FOLDERS; then
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
        # shellcheck disable=SC2086  # RUFF_FOLDERS is intentionally space-separated
        ruff format $RUFF_FOLDERS
        print_success "Code formatted with ruff"

        # Fix linting issues (including import sorting)
        # shellcheck disable=SC2086  # RUFF_FOLDERS is intentionally space-separated
        ruff check --fix $unsafe_flag $RUFF_FOLDERS
        if [ -n "$unsafe_flag" ]; then
            print_success "Code linting issues fixed with ruff (including unsafe fixes)"
        else
            print_success "Code linting issues fixed with ruff"
        fi

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
    local unsafe_param=""
    if [ "${1:-}" = "--unsafe" ]; then
        unsafe_param="--unsafe"
        print_header "Running all formatting fixes (including unsafe fixes)"
    else
        print_header "Running all formatting fixes"
    fi

    check_venv

    run_ruff "" "$unsafe_param"

    echo ""
    if [ -n "$unsafe_param" ]; then
        print_success "🎨 All formatting fixes applied (including unsafe fixes)!"
    else
        print_success "🎨 All formatting fixes applied!"
    fi

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
        --path|-p)
            if [ -z "${2:-}" ]; then
                print_error "Missing argument for $1"
                exit 1
            fi
            PROJECT_ROOT_OVERRIDE="$2"
            shift 2
            ;;
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
        --ruff-fix-unsafe)
            run_ruff "" --unsafe
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
        --fix-unsafe)
            run_format_fix --unsafe
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Code formatting script for BLE GATT Device"
            echo ""
            echo "OPTIONS:"
            echo "  --path, -p <path>    Run formatting in specified project path"
            echo "  --check             Check all formatting (default)"
            echo "  --fix               Fix all formatting issues"
            echo "  --fix-unsafe        Fix all formatting issues (including unsafe fixes)"
            echo ""
            echo "Ruff-based tools:"
            echo "  --ruff              Check ruff formatting and linting"
            echo "  --ruff-check        Check ruff formatting and linting"
            echo "  --ruff-fix          Fix ruff formatting and linting"
            echo "  --ruff-fix-unsafe   Fix ruff formatting and linting (including unsafe fixes)"
            echo ""
            echo "Examples:"
            echo "  $0                  # Check all formatting"
            echo "  $0 --check          # Check all formatting"
            echo "  $0 --fix            # Fix all formatting issues"
            echo "  $0 --fix-unsafe     # Fix all formatting issues (including unsafe)"
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
