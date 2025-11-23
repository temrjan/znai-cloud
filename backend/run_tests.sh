#!/bin/bash
# Script to run tests with proper configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running AI-Avangard Backend Tests${NC}"
echo "========================================"

# Check if we're in the backend directory
if [ ! -f "pytest.ini" ]; then
    echo -e "${RED}Error: pytest.ini not found. Please run this script from the backend directory.${NC}"
    exit 1
fi

# Check if dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${RED}pytest not found. Installing test dependencies...${NC}"
    pip install -r requirements-dev.txt
fi

# Run tests based on argument
case "$1" in
    unit)
        echo -e "${GREEN}Running unit tests only...${NC}"
        pytest tests/unit/ -v
        ;;
    integration)
        echo -e "${GREEN}Running integration tests only...${NC}"
        pytest tests/integration/ -v
        ;;
    coverage)
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    models)
        echo -e "${GREEN}Running organization models tests...${NC}"
        pytest tests/unit/test_models_organization.py -v
        ;;
    *)
        echo -e "${GREEN}Running all tests...${NC}"
        pytest -v
        ;;
esac

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Exit code: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
