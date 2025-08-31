#!/bin/bash
# Local formatting script that mirrors the CI formatting job
# Run this to format files locally without Docker containers

set -e

# Parse command line arguments
CHECK_MODE=false
if [ "$1" = "--check" ]; then
    CHECK_MODE=true
fi

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if we're running in CI or local environment
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    echo "🤖 Running in CI environment..."
    # In CI, Python and dependencies are already set up
    PYTHON_CMD="python"
else
    echo "💻 Running in local environment..."
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        echo "❌ Virtual environment not found. Please run:"
        echo "   python3 -m venv .venv"
        echo "   source .venv/bin/activate"
        echo "   pip install -e '.[dev]'"
        exit 1
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
    PYTHON_CMD="python"
fi

# Verify tools are available
echo "🔍 Checking formatting tools..."
$PYTHON_CMD -c "import black; print(f'✅ Black {black.__version__}')" || { echo "❌ Black not installed"; exit 1; }
$PYTHON_CMD -c "import isort; print(f'✅ isort {isort.__version__}')" || { echo "❌ isort not installed"; exit 1; }

echo ""
if [ "$CHECK_MODE" = true ]; then
    echo "🔍 Checking Black formatting (no changes will be made)..."
    $PYTHON_CMD -m black --check --diff src/ tests/
    
    echo ""
    echo "🔍 Checking isort import sorting (no changes will be made)..."
    $PYTHON_CMD -m isort --check-only --diff src/ tests/
    
    echo ""
    echo "✅ All files are properly formatted!"
else
    echo "🎨 Running Black formatting..."
    $PYTHON_CMD -m black src/ tests/

    echo ""
    echo "📦 Running isort import sorting..."
    $PYTHON_CMD -m isort src/ tests/

    echo ""
    echo "✅ Formatting complete!"

    # Show what changed
    if [ -n "$(git status --porcelain)" ]; then
        echo ""
        echo "📝 Files that were formatted:"
        git status --porcelain
        
        if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
            echo ""
            echo "ℹ️  Formatting was applied in CI environment."
        fi
    else
        echo ""
        echo "✨ No formatting changes needed - all files were already properly formatted!"
    fi
fi
