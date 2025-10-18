#!/bin/bash

set -euo pipefail

# Default to running all linting checks if no argument provided
if [ $# -eq 0 ]; then
    set -- --all
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# If user provided PROJECT_ROOT override, change to it
if [ -n "${PROJECT_ROOT_OVERRIDE:-}" ]; then
    # Resolve to absolute path
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

# Folders to lint/format
RUFF_FOLDERS="src/ tests/ examples/"
BLUETOOTH_SIG_FOLDERS="src/bluetooth_sig"
EXAMPLES_FOLDERS="examples"
TEST_FOLDERS="tests"

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

# Helper: run a command capturing stdout+stderr in $CAPTURE_OUTPUT and
# return its exit code without causing the script to exit (wraps set +e/-e).
run_capture() {
    CAPTURE_OUTPUT=""
    # Temporarily disable all error exit behaviors to properly capture command output
    local old_opts
    old_opts=$(set +o)
    set +euo pipefail
    CAPTURE_OUTPUT=$(eval "$*" 2>&1)
    local rc=$?
    # Restore original shell options
    eval "$old_opts"
    return $rc
}

# Check virtual environment
check_venv() {
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        print_warning "No virtual environment detected"
        # If the project has a local .venv, try to activate it automatically
        if [ -n "${PROJECT_ROOT:-}" ] && [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
            print_header "Attempting to activate project virtualenv: $PROJECT_ROOT/.venv"
            # shellcheck disable=SC1091
            # shellcheck source=/dev/null
            if source "$PROJECT_ROOT/.venv/bin/activate"; then
                print_success "Activated virtual environment: $VIRTUAL_ENV"
            else
                print_warning "Failed to activate virtualenv at $PROJECT_ROOT/.venv/bin/activate"
                print_warning "Consider running: source $PROJECT_ROOT/.venv/bin/activate"
            fi
        else
            if [ -n "${PROJECT_ROOT:-}" ]; then
                print_warning "Consider running: source $PROJECT_ROOT/.venv/bin/activate"
            else
                print_warning "Consider running: source .venv/bin/activate"
            fi
        fi
    else
        print_success "Virtual environment active: $VIRTUAL_ENV"
    fi
    echo ""
}

# Run ruff linting (replaces flake8)
# shellcheck disable=SC2120
run_ruff() {
    # Usage: run_ruff [is_parallel] [logfile]
    local is_parallel="${1:-false}"
    local _logfile="${2:-}"

    if [ "$is_parallel" != "true" ]; then
        print_header "Running ruff"
    fi

    if ! command -v ruff >/dev/null 2>&1; then
        print_error "ruff not found. Install with: pip install ruff"
        return 1
    fi

    # Run ruff and capture output, allowing it to fail
    local RUFF_OUTPUT
    # Enable caching for better performance
    # shellcheck disable=SC2086  # RUFF_FOLDERS is intentionally space-separated
    run_capture "ruff check --cache-dir .ruff_cache $RUFF_FOLDERS"
    local RUFF_EXIT_CODE=$?
    RUFF_OUTPUT="$CAPTURE_OUTPUT"

    if [ "$is_parallel" != "true" ]; then
        if [ $RUFF_EXIT_CODE -eq 0 ]; then
            print_success "ruff passed with zero violations"
            return 0
        else
            # Show the actual ruff output
            echo "$RUFF_OUTPUT"
            print_error "ruff found violations"
            return 1
        fi
    else
        # In parallel mode, always write the ruff output to logfile if provided
        if [ -n "${_logfile}" ]; then
            # Write atomically: use a temp file then move into place
            tmpfile="${_logfile}.$$.$RANDOM.tmp"
            printf "%s\n" "$RUFF_OUTPUT" >"$tmpfile" || true
            mv "$tmpfile" "$_logfile" || true
        fi
        # Also output to stdout for spawn_bg to capture
        if [ $RUFF_EXIT_CODE -ne 0 ]; then
            echo "=== RUFF OUTPUT ==="
            echo "$RUFF_OUTPUT"
            echo "=== END RUFF OUTPUT ==="
        fi
        if [ $RUFF_EXIT_CODE -ne 0 ]; then
            return 1
        fi
        return 0
    fi
}


# Run pylint
# shellcheck disable=SC2120
run_pylint() {
    # Usage: run_pylint [is_parallel] [logfile]
    local is_parallel="${1:-false}"
    local _logfile="${2:-}"

    if [ "$is_parallel" != "true" ]; then
        print_header "Running pylint"
    fi

    if ! command -v pylint >/dev/null 2>&1; then
        print_error "pylint not found. Install with: pip install pylint"
        return 1
    fi

    local exit_code=0
    local production_failed=0
    local tests_failed=0

    # Run pylint on production code (strict requirements)
    if [ "$is_parallel" != "true" ]; then
        echo "Checking production code..."
    fi
    # Use persistent cache for better performance
    # shellcheck disable=SC2086  # BLUETOOTH_SIG_FOLDERS is intentionally space-separated
    run_capture "pylint --persistent=n $BLUETOOTH_SIG_FOLDERS"
    PROD_PYLINT_OUTPUT="$CAPTURE_OUTPUT"

    # Extract production score
    PROD_SCORE=$(echo "$PROD_PYLINT_OUTPUT" | sed -n 's/.*rated at \([0-9]\+\.[0-9]\+\).*/\1/p' | head -1)

    if [ "$is_parallel" != "true" ]; then
        echo "Production pylint score: $PROD_SCORE/10"
    fi

    # Production code must be perfect
    if [ "$PROD_SCORE" != "10.00" ]; then
        if [ "$is_parallel" != "true" ]; then
            print_error "Production pylint score must be exactly 10.00/10. Current score: $PROD_SCORE/10"
            echo "Please fix all pylint issues in production code or add justified disable comments."
        fi
        exit_code=1
        production_failed=1
    else
        if [ "$is_parallel" != "true" ]; then
            print_success "Production code achieved perfect pylint score: 10.00/10"
        fi
    fi

    if [ "$is_parallel" != "true" ]; then
        echo ""
    fi

    # Run pylint on tests (ignore common test-specific issues - see detailed comments below)
    if [ "$is_parallel" != "true" ]; then
        echo "Checking test code..."
    fi
    local TEST_PYLINT_OUTPUT
    # Temporarily allow pylint to fail for test-specific disabled checks
    # Disabled pylint checks for test files (acceptable for test code):
    # C0114: missing-module-docstring - Test modules often don't need docstrings
    # C0115: missing-class-docstring - Test classes often don't need docstrings
    # C0116: missing-function-docstring - Test methods often don't need docstrings
    # W0212: protected-access - Tests frequently access private/protected members
    # C0415: import-outside-toplevel - Tests may import conditionally or inside functions
    # W0718: broad-exception-caught - Tests may catch broad exceptions for robustness
    # R0914: too-many-locals - Complex tests may need many local variables
    # R0912: too-many-branches - Test logic may have many conditional branches
    # R0915: too-many-statements - Test setup/verification may have many statements
    # R1702: too-many-nested-blocks - Test logic may be deeply nested
    # C1803: use-implicit-booleaness-not-comparison - Tests may use dict == {} instead of not dict
    # W0105: pointless-string-statement - Tests may have string literals for debugging
    # R0903: too-few-public-methods - Test classes may have few public methods
    # W0201: attribute-defined-outside-init - Test attributes set in setup methods
    # W0621: redefined-outer-name - Tests may shadow variable names
    # W0404: reimported - Tests may reimport modules
    # W0221: arguments-differ - Test methods may have different signatures than base
    # E0401: import-error - Tests may import modules that aren't available in test environment
    # R0801: duplicate-code - Test fixtures may have similar boilerplate code
    run_capture "pylint --persistent=n --disable=C0114,C0115,C0116,W0212,C0415,W0718,W0613,R0914,R0912,R0915,R1702,C1803,W0105,R0903,W0201,W0621,W0404,W0221,E0401,R0801 $TEST_FOLDERS $EXAMPLES_FOLDERS"
    local TEST_PYLINT_EXIT_CODE=$?
    TEST_PYLINT_OUTPUT="$CAPTURE_OUTPUT"
    local TEST_PYLINT_HAS_MESSAGES=0
    if printf '%s\n' "$TEST_PYLINT_OUTPUT" | grep -Eq ':[[:space:]]*\[[A-Z]'; then
        TEST_PYLINT_HAS_MESSAGES=1
    fi
    if [ $TEST_PYLINT_EXIT_CODE -ne 0 ]; then
        tests_failed=1
    fi

    # Always show detailed test output in non-parallel mode
    if [ "$is_parallel" != "true" ]; then
        echo "Test pylint output (ignoring common test issues):"
        echo "$TEST_PYLINT_OUTPUT"
    else
        # In parallel mode, write a combined pylint report to the logfile so
        # both production and test outputs (and approximate exit statuses)
        # are always present. This avoids partial logfile contents when the
        # helper runs in a background subshell.
        if [ -n "${_logfile}" ]; then
            tmpfile="${_logfile}.$$.$RANDOM.tmp"
            {
                printf "=== PYLINT: production ===\n"
                printf "%s\n" "$PROD_PYLINT_OUTPUT"
                printf "\n=== PYLINT: tests (common issues ignored) ===\n"
                printf "%s\n" "$TEST_PYLINT_OUTPUT"
                printf "\n=== PYLINT: summary ===\n"
                printf "production_score=%s\n" "${PROD_SCORE:-unknown}"
                printf "test_exit_code=%s\n" "${TEST_PYLINT_EXIT_CODE:-unknown}"
                printf "test_messages_present=%s\n" "${TEST_PYLINT_HAS_MESSAGES:-0}"
            } >"$tmpfile" || true
            mv "$tmpfile" "$_logfile" || true
        fi
        # Also output to stdout for spawn_bg to capture when there are errors
        if [ $production_failed -eq 1 ] || [ $tests_failed -eq 1 ]; then
            echo "=== PYLINT OUTPUT ==="
            if [ $production_failed -eq 1 ]; then
                echo "Production pylint score: $PROD_SCORE/10 (must be 10.00)"
                echo "$PROD_PYLINT_OUTPUT"
            fi
            if [ $tests_failed -eq 1 ]; then
                echo "Test pylint issues:"
                echo "$TEST_PYLINT_OUTPUT"
            fi
            echo "=== END PYLINT OUTPUT ==="
        fi
    fi

    # Check if pylint passed after disabling common issues
    if [ $TEST_PYLINT_EXIT_CODE -ne 0 ]; then
        if [ "$is_parallel" != "true" ]; then
            print_error "Test code has pylint issues even after disabling common test-specific checks"
        fi
        exit_code=1
    else
        if [ "$is_parallel" != "true" ]; then
            print_success "Test code passed pylint checks (common test issues ignored)"
        fi
        if [ $TEST_PYLINT_HAS_MESSAGES -eq 1 ] && [ "$is_parallel" != "true" ]; then
            print_warning "pylint reported warnings/errors in tests/examples"
        fi
    fi

    return $exit_code
}

# Run mypy type checking
# shellcheck disable=SC2120
run_mypy() {
    # Usage: run_mypy [is_parallel] [logfile]
    local is_parallel="${1:-false}"
    local _logfile="${2:-}"

    if [ "$is_parallel" != "true" ]; then
        print_header "Running mypy type checking"
    fi

    if ! command -v mypy >/dev/null 2>&1; then
        if [ "$is_parallel" != "true" ]; then
            print_warning "mypy not found. Install with: pip install mypy"
            print_warning "Skipping type checking"
        fi
        return 0
    fi

    local exit_code=0

    # Run mypy on production code (strict) using package-based invocation and
    # explicit package bases so mypy maps the `src/` layout consistently and
    # avoids "source file found twice" errors.
    if [ "$is_parallel" != "true" ]; then
        echo "Checking production code types..."
    fi
    local PROD_MYPY_OUTPUT
    # Use cache for better performance and -p flag to check specific package
    run_capture "MYPYPATH=src python -m mypy --cache-dir=.mypy_cache --explicit-package-bases --config-file pyproject.toml -p bluetooth_sig"
    local PROD_MYPY_EXIT_CODE=$?
    PROD_MYPY_OUTPUT="$CAPTURE_OUTPUT"

    if [ "$is_parallel" != "true" ]; then
        if [ $PROD_MYPY_EXIT_CODE -eq 0 ]; then
            print_success "Production code type checking passed"
        else
            print_error "Production code type checking failed"
            echo "$PROD_MYPY_OUTPUT"
            exit_code=1
        fi
    else
        if [ -n "${_logfile}" ]; then
            tmpfile="${_logfile}.$$.$RANDOM.tmp"
            {
                printf "=== MYPY: production ===\n"
                printf "%s\n" "$PROD_MYPY_OUTPUT"
            } >"$tmpfile" || true
            mv "$tmpfile" "$_logfile" || true
        fi
        # Also output to stdout for spawn_bg to capture when there are errors
        if [ $PROD_MYPY_EXIT_CODE -ne 0 ]; then
            echo "=== MYPY PRODUCTION OUTPUT ==="
            echo "$PROD_MYPY_OUTPUT"
            echo "=== END MYPY PRODUCTION OUTPUT ==="
        fi
        if [ $PROD_MYPY_EXIT_CODE -ne 0 ]; then
            exit_code=1
        fi
    fi

    if [ "$is_parallel" != "true" ]; then
        echo ""
    fi

    # Run mypy on examples (lenient - examples are demonstration code)
    if [ "$is_parallel" != "true" ]; then
        echo "Checking example code types..."
    fi
    # Run mypy but don't fail on errors (examples are allowed to have type issues)
    # shellcheck disable=SC2086  # EXAMPLES_FOLDERS is intentionally space-separated
    run_capture "MYPYPATH=src python -m mypy --cache-dir=.mypy_cache --explicit-package-bases --config-file pyproject.toml $EXAMPLES_FOLDERS"
    local EXAMPLES_MYPY_EXIT_CODE=$?
    local EXAMPLES_MYPY_OUTPUT="$CAPTURE_OUTPUT"

    if [ "$is_parallel" != "true" ]; then
        if [ $EXAMPLES_MYPY_EXIT_CODE -eq 0 ]; then
            print_success "Example code type checking passed"
        else
            print_error "Example code type checking found issues"
            echo "$EXAMPLES_MYPY_OUTPUT"
            exit_code=1
        fi
    else
        if [ -n "${_logfile}" ]; then
            {
                printf "\n=== MYPY: examples ===\n"
                printf "%s\n" "$EXAMPLES_MYPY_OUTPUT"
            } >>"$_logfile"
            # If appending, ensure atomicity by appending to a tmp and then
            # concatenating. Simpler approach: append to final file as above
            # but ensure parent waits on PID before reading. Keep as append.
        fi
        # Also output to stdout for spawn_bg to capture when there are errors
        if [ $EXAMPLES_MYPY_EXIT_CODE -ne 0 ]; then
            echo "=== MYPY EXAMPLES OUTPUT ==="
            echo "$EXAMPLES_MYPY_OUTPUT"
            echo "=== END MYPY EXAMPLES OUTPUT ==="
            exit_code=1
        fi
    fi

    if [ "$is_parallel" != "true" ]; then
        echo ""
    fi

    # Run mypy on tests (lenient - tests often have type issues due to mocking, fixtures, etc.)
    if [ "$is_parallel" != "true" ]; then
        echo "Checking test code types..."
    fi
    # Run mypy but don't fail on errors (tests are allowed to have type issues)
    # shellcheck disable=SC2086  # TEST_FOLDERS is intentionally space-separated
    # Use PYTHONPATH="" to avoid duplicate source issues
    run_capture "PYTHONPATH=\"\" python -m mypy --cache-dir=.mypy_cache --config-file pyproject.toml $TEST_FOLDERS"
    local TEST_MYPY_EXIT_CODE=$?
    local TEST_MYPY_OUTPUT="$CAPTURE_OUTPUT"

    if [ "$is_parallel" != "true" ]; then
        if [ $TEST_MYPY_EXIT_CODE -eq 0 ]; then
            print_success "Test code type checking passed"
        else
            print_error "Test code type checking found issues"
            echo "$TEST_MYPY_OUTPUT"
            exit_code=1
        fi
    else
        if [ -n "${_logfile}" ]; then
            {
                printf "\n=== MYPY: tests ===\n"
                printf "%s\n" "$TEST_MYPY_OUTPUT"
            } >>"$_logfile"
                # As above, tests appended to logfile. The helper uses mv for the
                # initial production section; subsequent appends are OK because
                # the parent waits on PID before reading the file.
        fi
        # Also output to stdout for spawn_bg to capture when there are errors
        if [ $TEST_MYPY_EXIT_CODE -ne 0 ]; then
            echo "=== MYPY TESTS OUTPUT ==="
            echo "$TEST_MYPY_OUTPUT"
            echo "=== END MYPY TESTS OUTPUT ==="
            exit_code=1
        fi
    fi

    return $exit_code
}

# Run shellcheck
# shellcheck disable=SC2120
run_shellcheck() {
    # Usage: run_shellcheck [is_parallel] [logfile]
    local is_parallel="${1:-false}"
    local _logfile="${2:-}"

    if [ "$is_parallel" != "true" ]; then
        print_header "Running shellcheck"
    fi

    if ! command -v shellcheck >/dev/null 2>&1; then
        if [ "$is_parallel" != "true" ]; then
            print_warning "shellcheck not found. Install with: apt-get install shellcheck or brew install shellcheck"
            print_warning "Skipping shellcheck checks (not installed on this machine)"
        fi
        return 0
    fi

    # Find all shell scripts in the project
    local shell_scripts
    shell_scripts=$(find . -name "*.sh" -type f | grep -v ".venv" | head -20)

    if [ -z "$shell_scripts" ]; then
        if [ "$is_parallel" != "true" ]; then
            print_warning "No shell scripts found to check"
        fi
        return 0
    fi

    if [ "$is_parallel" != "true" ]; then
        echo "Checking shell scripts:"
        echo "$shell_scripts"
        echo ""
    fi

    # Run shellcheck on all shell scripts
    local exit_code=0
    local total_issues=0

    while IFS= read -r script; do
        if [ -n "$script" ]; then
            if [ "$is_parallel" != "true" ]; then
                echo "Checking: $script"
            fi

            # Run shellcheck, allowing it to fail; capture output so we don't run it twice
            run_capture "shellcheck \"$script\""
            local script_exit_code=$?

            if [ $script_exit_code -ne 0 ]; then
                exit_code=1
                # In non-parallel mode, show shellcheck output for the script
                if [ "$is_parallel" != "true" ]; then
                    echo "Shellcheck output for: $script"
                    printf "%s\n" "$CAPTURE_OUTPUT"
                else
                    # In parallel mode, append the script's output into the provided logfile
                    if [ -n "${_logfile}" ]; then
                                # Append each script's output; rely on parent wait to
                                # only read logfile after background job completes.
                                {
                                    printf "=== SHELLCHECK: %s ===\n" "$script"
                                    printf "%s\n" "$CAPTURE_OUTPUT"
                                    printf "\n"
                                } >>"$_logfile" || true
                    fi
                    # Also output to stdout for spawn_bg to capture
                    echo "=== SHELLCHECK ERROR: $script ==="
                    printf "%s\n" "$CAPTURE_OUTPUT"
                    echo "=== END SHELLCHECK ERROR ==="
                fi
                # Count issues for this script from captured output
                local script_issues
                script_issues=$(printf "%s" "$CAPTURE_OUTPUT" | grep -c "^In " || true)
                total_issues=$((total_issues + script_issues))
            fi
            if [ "$is_parallel" != "true" ]; then
                echo ""
            fi
        fi
    done <<< "$shell_scripts"

    if [ "$is_parallel" != "true" ]; then
        if [ $exit_code -eq 0 ]; then
            print_success "shellcheck passed with zero issues"
            return 0
        else
            print_error "shellcheck found $total_issues issues"
            echo "Please fix shellcheck issues or add shellcheck disable comments where justified."
            return 1
        fi
    else
        # In parallel mode, return the result without printing
        return $exit_code
    fi
}

# Run pydocstyle
run_pydocstyle() {
    # Usage: run_pydocstyle [is_parallel] [logfile]
    local is_parallel="${1:-false}"
    local _logfile="${2:-}"

    if [ "$is_parallel" != "true" ]; then
        print_header "Running pydocstyle"
    fi

    if ! command -v pydocstyle >/dev/null 2>&1; then
        print_error "pydocstyle not found. Install with: pip install pydocstyle"
        return 1
    fi

    # Run pydocstyle only on source code (tests are excluded
    # because they intentionally contain many informal helpers
    # scripts that don't require exhaustive Google-style docstrings).
    local PYDOCSTYLE_FOLDERS="src examples"
    local PYDOCSTYLE_OUTPUT
    # shellcheck disable=SC2086  # PYDOCSTYLE_FOLDERS is intentionally space-separated
    run_capture "pydocstyle --convention=google $PYDOCSTYLE_FOLDERS"
    local PYDOCSTYLE_EXIT_CODE=$?
    PYDOCSTYLE_OUTPUT="$CAPTURE_OUTPUT"

    if [ "$is_parallel" != "true" ]; then
        if [ $PYDOCSTYLE_EXIT_CODE -eq 0 ]; then
            print_success "pydocstyle passed with zero violations"
            return 0
        else
            # Show the actual pydocstyle output
            echo "$PYDOCSTYLE_OUTPUT"
            print_error "pydocstyle found violations"
            return 1
        fi
    else
        # In parallel mode, always write the pydocstyle output to logfile if provided
        if [ -n "${_logfile}" ]; then
            # Write atomically: use a temp file then move into place
            tmpfile="${_logfile}.$$.$RANDOM.tmp"
            printf "%s\n" "$PYDOCSTYLE_OUTPUT" >"$tmpfile" || true
            mv "$tmpfile" "$_logfile" || true
        fi
        # Also output to stdout for spawn_bg to capture
        if [ $PYDOCSTYLE_EXIT_CODE -ne 0 ]; then
            echo "=== PYDOCSTYLE OUTPUT ==="
            echo "$PYDOCSTYLE_OUTPUT"
            echo "=== END PYDOCSTYLE OUTPUT ==="
        fi
        if [ $PYDOCSTYLE_EXIT_CODE -ne 0 ]; then
            return 1
        fi
        return 0
    fi
}

# Run all linting checks
run_all_checks() {
    print_header "Running all linting checks"
    local exit_code=0

    check_venv

    # Check if sequential execution is requested (parallel is default)
    if [ "${BLE_LINT_SEQUENTIAL:-0}" = "1" ]; then
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

        if ! run_pydocstyle false ""; then
            exit_code=1
        fi

        echo ""

        if [ $exit_code -eq 0 ]; then
            print_success "🚀 All linting checks passed!"
        else
            print_error "💥 Some linting checks failed"
        fi

        return $exit_code
    else
        run_all_checks_parallel
        return $?
    fi
}

# Run all linting checks in parallel for maximum speed
run_all_checks_parallel() {
    print_header "Running all linting checks (parallel mode)"
    echo "Starting comprehensive linting checks in parallel..."

    # Detect available CPU cores and fall back to 2
    CORES=$(nproc --all 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 2)
    echo "Detected CPU cores: $CORES"

    # Helper: wait for pid, print a named result and update exit_code
    # Accepts an optional third argument: logfile path to display on failure
    wait_and_report() {
        local pid=$1
        local name="$2"
        local logfile="$3"
        local code
        # avoid exiting the whole script if the waited-for process fails
        set +e
        wait "$pid"
        code=$?
        set -e
        if [ $code -eq 0 ]; then
            print_success "$name passed"
            if [ -n "${logfile:-}" ] && [ -f "$logfile" ] && [ "$name" = "pylint" ]; then
                if grep -q 'test_messages_present=1' "$logfile"; then
                    print_warning "pylint reported warnings/errors in tests/examples"
                    sed -n '1,200p' "$logfile" || true
                fi
            fi
        else
            print_error "$name failed"
            exit_code=1
            # If logfile exists, print a helpful excerpt for debugging
            if [ -n "${logfile:-}" ] && [ -f "$logfile" ]; then
                echo "--- Begin $name output ($logfile) ---"
                sed -n '1,200p' "$logfile" || true
                echo "--- End $name output ---"
            fi
        fi
    }

    local exit_code=0

    # Create a temporary log directory for parallel runs so we can surface
    # tool output on failure without flooding the console on success.
    # Create a log directory. Use mktemp where available, otherwise fall back
    # to a timestamped directory to avoid mktemp implementation differences.
    LOGDIR=""
    if LOGDIR=$(mktemp -d "${PROJECT_ROOT}/.lint_logs.XXXX" 2>/dev/null); then
        :
    else
        LOGDIR="${PROJECT_ROOT}/.lint_logs.$(date +%s%N)"
        mkdir -p "$LOGDIR"
    fi
    export LOGDIR

    # Set up cleanup trap to remove temporary directory on exit/interrupt
    cleanup_logdir() {
        if [ -n "${LOGDIR:-}" ] && [ -d "$LOGDIR" ]; then
            rm -rf "$LOGDIR" 2>/dev/null || true
        fi
    }
    trap cleanup_logdir EXIT INT TERM

    echo "Writing parallel lint logs to: $LOGDIR"

    # Spawn each check as a backgrounded invocation of the existing helper
    # functions so the parallel and sequential paths use the same code.
    spawn_bg() {
        # spawn_bg <function_name> <logfile> <pidfile>
        local func="$1"
        local logfile="$2"
        local pidfile="$3"

        # Run the function in a subshell with proper output redirection
        # The helper functions are responsible for writing their output to logfile
        # in parallel mode, but we also capture any stdout/stderr here as backup
        (
            set +e
            # Call the function with parallel mode and logfile
            $func true "$logfile" >"${logfile}.stdout" 2>"${logfile}.stderr"
            local rc=$?
            # Combine any stdout/stderr with the main logfile for complete output
            if [ -s "${logfile}.stdout" ] || [ -s "${logfile}.stderr" ]; then
                {
                    if [ -s "${logfile}.stdout" ]; then
                        echo "=== STDOUT ==="
                        cat "${logfile}.stdout"
                    fi
                    if [ -s "${logfile}.stderr" ]; then
                        echo "=== STDERR ==="
                        cat "${logfile}.stderr"
                    fi
                } >> "$logfile"
            fi
            # Clean up temporary files
            rm -f "${logfile}.stdout" "${logfile}.stderr"
            exit $rc
        ) &

        # Write PID to pidfile for parent to track
        printf "%s" "$!" >"$pidfile"
    }

    # Start backgrounded helper functions and capture pids via pidfiles
    spawn_bg run_ruff "$LOGDIR/ruff.out" "$LOGDIR/ruff.pid"
    spawn_bg run_pylint "$LOGDIR/pylint.out" "$LOGDIR/pylint.pid"
    spawn_bg run_mypy "$LOGDIR/mypy.out" "$LOGDIR/mypy.pid"
    spawn_bg run_shellcheck "$LOGDIR/shellcheck.out" "$LOGDIR/shellcheck.pid"
    spawn_bg run_pydocstyle "$LOGDIR/pydocstyle.out" "$LOGDIR/pydocstyle.pid"

    pid_ruff=$(cat "$LOGDIR/ruff.pid")
    pid_pylint=$(cat "$LOGDIR/pylint.pid")
    pid_mypy=$(cat "$LOGDIR/mypy.pid")
    pid_shellcheck=$(cat "$LOGDIR/shellcheck.pid")
    pid_pydocstyle=$(cat "$LOGDIR/pydocstyle.pid")

    echo "⏳ Running comprehensive checks in parallel (ruff, pylint(prod/examples/test), mypy(prod/examples/tests), shellcheck, pydocstyle)..."

    # Wait & report using the helper to reduce duplication
    wait_and_report "$pid_ruff" "ruff" "$LOGDIR/ruff.out"
    wait_and_report "$pid_pylint" "pylint" "$LOGDIR/pylint.out"
    wait_and_report "$pid_mypy" "mypy" "$LOGDIR/mypy.out"
    wait_and_report "$pid_shellcheck" "shellcheck" "$LOGDIR/shellcheck.out"
    wait_and_report "$pid_pydocstyle" "pydocstyle" "$LOGDIR/pydocstyle.out"

    echo ""

    if [ $exit_code -eq 0 ]; then
        print_success "🚀 All comprehensive linting checks passed!"
    else
        print_error "💥 Some linting checks failed"
    fi

    # Explicit cleanup of temporary log directory
    cleanup_logdir

    return $exit_code
}

# Parse command line arguments
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
        --all|--check)
            run_all_checks
            exit $?
            ;;
        --parallel)
            # Parallel is now the default, but keep this option for compatibility
            run_all_checks
            exit $?
            ;;
        --sequential)
            BLE_LINT_SEQUENTIAL=1 run_all_checks
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
        --doc)
            check_venv
            run_pydocstyle
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [OPTION]"
            echo ""
            echo "Code linting script for BLE GATT Device"
            echo ""
            echo "OPTIONS:"
            echo "  --all, --check      Run all linting checks in parallel (default - fastest)"
            echo "  --sequential        Run all linting checks sequentially with detailed output (slower)"
            echo "  --parallel          Same as --all (parallel mode for speed)"
            echo "  --path, -p <path>   Run checks in specified project path"
            echo ""
            echo "Individual tools:"
            echo "  --ruff              Run ruff linting (replaces flake8)"
            echo "  --pylint            Run pylint analysis (production: 10.00/10, tests: ignores common test issues)"
            echo "  --mypy              Run mypy type checking (production: strict, tests: lenient)"
            echo "  --shellcheck        Run shellcheck shell script analysis"
            echo "  --doc               Run pydocstyle docstring analysis (Google style)"
            echo ""
            echo "Examples:"
            echo "  $0                  # Run all comprehensive checks in parallel (~16s - fastest)"
            echo "  $0 --all            # Same as above (parallel by default)"
            echo "  $0 --sequential     # Run all comprehensive checks sequentially (~17s - with detailed output)"
            echo "  $0 --ruff           # Run only ruff"
            echo "  $0 --pylint         # Run only pylint"
            echo "  $0 --mypy           # Run only mypy"
            echo "  $0 --shellcheck     # Run only shellcheck"
            echo "  $0 --doc     # Run only pydocstyle"
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