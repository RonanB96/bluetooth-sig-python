#!/bin/bash

set -euo pipefail

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

# Check if mypy is available
if ! command -v mypy >/dev/null 2>&1; then
    print_warning "mypy not found. Install with: pip install mypy"
    print_warning "Skipping type checking"
    exit 0
fi

print_header "Running mypy type checking"

# Run mypy on source code
if mypy src/bluetooth_sig --config-file mypy.ini; then
    print_success "mypy type checking passed"
else
    print_error "mypy type checking failed"
    echo ""
    echo "Run with --show-error-codes for more details:"
    echo "  mypy src/bluetooth_sig --config-file mypy.ini --show-error-codes"
    exit 1
fi