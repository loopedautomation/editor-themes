#!/bin/bash
# Run theme format tests

set -e

echo "🧪 Running theme format tests..."
python -m pytest tests/ -v "$@"

echo ""
echo "✅ All tests passed!"
