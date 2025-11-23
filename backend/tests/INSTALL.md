# Installation and Setup Guide

## Prerequisites

- Python 3.12+
- pip

## Installation

### 1. Navigate to backend directory
```bash
cd /home/temrjan/ai-avangard/backend
```

### 2. Install dependencies

#### Production dependencies
```bash
pip install -r requirements.txt
```

#### Development dependencies (including test tools)
```bash
pip install -r requirements-dev.txt
```

Or install all at once:
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Verify installation

Check that pytest is installed:
```bash
pytest --version
```

Expected output:
```
pytest 8.3.4
```

## Running Tests

### Option 1: Using the provided script (recommended)
```bash
./run_tests.sh
```

Available options:
- `./run_tests.sh` - Run all tests
- `./run_tests.sh unit` - Run unit tests only
- `./run_tests.sh models` - Run organization models tests
- `./run_tests.sh coverage` - Run with coverage report

### Option 2: Using pytest directly
```bash
# All tests
pytest

# Verbose output
pytest -v

# Very verbose
pytest -vv

# Specific file
pytest tests/unit/test_models_organization.py

# Specific test class
pytest tests/unit/test_models_organization.py::TestOrganizationModel

# Specific test
pytest tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization

# With coverage
pytest --cov=app --cov-report=html
```

## Expected Output

Successful run should look like:
```
========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 33 items

tests/unit/test_models_organization.py ........................... [100%]

========================== 33 passed in 2.45s ===========================
```

## Troubleshooting

### ModuleNotFoundError: No module named 'backend'

**Solution**: Make sure you're in the backend directory
```bash
cd /home/temrjan/ai-avangard/backend
pytest
```

### ModuleNotFoundError: No module named 'pytest'

**Solution**: Install development dependencies
```bash
pip install -r requirements-dev.txt
```

### ModuleNotFoundError: No module named 'aiosqlite'

**Solution**: Install aiosqlite
```bash
pip install aiosqlite==0.20.0
```

Or reinstall dev dependencies:
```bash
pip install -r requirements-dev.txt
```

### Permission denied: ./run_tests.sh

**Solution**: Make script executable
```bash
chmod +x run_tests.sh
./run_tests.sh
```

### Tests fail with database errors

**Solution**: Check that:
1. aiosqlite is installed
2. SQLAlchemy is version 2.0.36+
3. pytest-asyncio is installed
4. You're running from backend directory

## Next Steps

1. **Read the documentation**:
   - `tests/README.md` - General overview
   - `TESTING_QUICK_START.md` - Quick reference
   - `tests/TESTING_GUIDE.md` - Detailed guide

2. **Run tests with coverage**:
   ```bash
   ./run_tests.sh coverage
   open htmlcov/index.html  # View coverage report
   ```

3. **Write new tests**:
   - Use existing tests as templates
   - Follow AAA pattern (Arrange, Act, Assert)
   - Use fixtures from `conftest.py`
   - Mark async tests with `@pytest.mark.asyncio`

## CI/CD Integration

For GitHub Actions:
```yaml
- name: Install dependencies
  run: |
    cd backend
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml
```

## Getting Help

1. Check `tests/TESTING_GUIDE.md` - Troubleshooting section
2. Check `tests/EXAMPLE_OUTPUT.md` - See expected outputs
3. Review test code in `tests/unit/test_models_organization.py`
