# Backend Tests

This directory contains all tests for the AI-Avangard backend application.

## Structure

```
tests/
├── unit/                          # Unit tests
│   └── test_models_organization.py  # Organization models tests
└── integration/                   # Integration tests
```

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

Run all tests:
```bash
pytest
```

Run unit tests only:
```bash
pytest tests/unit/
```

Run specific test file:
```bash
pytest tests/unit/test_models_organization.py
```

Run specific test class:
```bash
pytest tests/unit/test_models_organization.py::TestOrganizationModel
```

Run specific test:
```bash
pytest tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization
```

### Test Coverage

Generate coverage report:
```bash
pytest --cov=app --cov-report=html
```

View coverage in browser:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Verbose Output

```bash
pytest -v  # verbose
pytest -vv  # very verbose
pytest -s  # show print statements
```

## Unit Tests

### test_models_organization.py

Tests for organization-related SQLAlchemy models:

**TestOrganizationModel**
- `test_create_organization` - Organization creation with default values
- `test_organization_required_fields` - Required fields validation
- `test_organization_unique_slug` - Unique slug constraint
- `test_organization_relationships` - Owner and members relationships
- `test_organization_status_enum` - Status enum values
- `test_organization_custom_quotas` - Custom quota settings

**TestOrganizationInviteModel**
- `test_create_invite` - Invite creation with UUID code
- `test_invite_unique_code` - Unique invite codes
- `test_invite_validation` - Max uses validation
- `test_invite_expiration` - Expiration handling
- `test_invite_status_changes` - Status transitions
- `test_invite_relationships` - Organization and creator relationships

**TestOrganizationMemberModel**
- `test_organization_member_history` - Member history tracking
- `test_member_with_inviter` - Inviter information
- `test_member_leave_organization` - Member departure
- `test_member_role_types` - Different role types

**TestOrganizationSettingsModel**
- `test_organization_settings_defaults` - Default values
- `test_settings_llm_configuration` - LLM settings
- `test_settings_jsonb_fields` - JSONB fields (terminology, filters)
- `test_settings_document_processing` - Chunk size/overlap
- `test_settings_language_configuration` - Language settings
- `test_settings_citation_configuration` - Citation settings
- `test_settings_relationship` - Organization relationship

**TestUserOrganizationFields**
- `test_user_organization_fields` - Organization-related user fields
- `test_user_platform_admin` - Platform admin flag
- `test_user_without_organization` - Users without organization

**TestDocumentVisibility**
- `test_document_visibility` - Document visibility levels
- `test_document_private_visibility` - Private documents
- `test_document_organization_relationship` - Organization relationships
- `test_document_default_visibility` - Default visibility

**TestCascadeDeletes**
- `test_organization_delete_cascades` - Cascade delete behavior

## Writing Tests

### Test Structure

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

class TestMyFeature:
    @pytest.mark.asyncio
    async def test_something(self, db_session: AsyncSession):
        # Arrange
        data = {"key": "value"}

        # Act
        result = await some_function(db_session, data)

        # Assert
        assert result.success is True
```

### Fixtures

Common fixtures available:
- `engine` - Async SQLAlchemy engine (in-memory SQLite)
- `db_session` - Async database session
- `test_user` - Pre-created test user
- `test_organization` - Pre-created test organization

### Best Practices

1. **Independence**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use fixtures that auto-rollback to clean up after tests
3. **Async**: Use `@pytest.mark.asyncio` for async tests
4. **Naming**: Use descriptive test names that explain what is being tested
5. **AAA Pattern**: Arrange, Act, Assert structure
6. **Assertions**: Use specific assertions with clear error messages

### Example Test

```python
@pytest.mark.asyncio
async def test_create_organization(self, db_session: AsyncSession, test_user: User):
    """Test creating an organization with default values."""
    # Arrange
    org_data = {
        "name": "New Organization",
        "slug": "new-org",
        "owner_id": test_user.id
    }

    # Act
    org = Organization(**org_data)
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # Assert
    assert org.id is not None
    assert org.max_members == 10  # default value
    assert org.status == OrganizationStatus.ACTIVE
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pytest --cov=app --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the backend directory is in PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/znai-cloud/backend"
```

Or run from the backend directory:
```bash
cd backend
pytest
```

### Database Errors

Tests use in-memory SQLite by default. If you see database errors:
1. Check that `aiosqlite` is installed
2. Verify SQLAlchemy models are compatible with SQLite
3. Check that foreign key constraints are properly defined

### Async Errors

If async tests fail:
1. Ensure `pytest-asyncio` is installed
2. Check `asyncio_mode = auto` in pytest.ini
3. Use `@pytest.mark.asyncio` decorator

## Contributing

When adding new tests:
1. Follow existing test structure
2. Add docstrings to test functions
3. Use descriptive test names
4. Ensure tests are independent
5. Update this README if adding new test categories
