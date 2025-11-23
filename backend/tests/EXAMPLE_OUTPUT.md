# Примеры вывода тестов

## Успешный запуск всех тестов

```bash
$ ./run_tests.sh models

Running AI-Avangard Backend Tests
========================================
Running organization models tests...

========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 33 items

tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization PASSED [  3%]
tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_required_fields PASSED [  6%]
tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_unique_slug PASSED [  9%]
tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_relationships PASSED [ 12%]
tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_status_enum PASSED [ 15%]
tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_custom_quotas PASSED [ 18%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_create_invite PASSED [ 21%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_invite_unique_code PASSED [ 24%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_invite_validation PASSED [ 27%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_invite_expiration PASSED [ 30%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_invite_status_changes PASSED [ 33%]
tests/unit/test_models_organization.py::TestOrganizationInviteModel::test_invite_relationships PASSED [ 36%]
tests/unit/test_models_organization.py::TestOrganizationMemberModel::test_organization_member_history PASSED [ 39%]
tests/unit/test_models_organization.py::TestOrganizationMemberModel::test_member_with_inviter PASSED [ 42%]
tests/unit/test_models_organization.py::TestOrganizationMemberModel::test_member_leave_organization PASSED [ 45%]
tests/unit/test_models_organization.py::TestOrganizationMemberModel::test_member_role_types PASSED [ 48%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_organization_settings_defaults PASSED [ 51%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_llm_configuration PASSED [ 54%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_jsonb_fields PASSED [ 57%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_document_processing PASSED [ 60%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_language_configuration PASSED [ 63%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_citation_configuration PASSED [ 66%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_relationship PASSED [ 69%]
tests/unit/test_models_organization.py::TestUserOrganizationFields::test_user_organization_fields PASSED [ 72%]
tests/unit/test_models_organization.py::TestUserOrganizationFields::test_user_platform_admin PASSED [ 75%]
tests/unit/test_models_organization.py::TestUserOrganizationFields::test_user_without_organization PASSED [ 78%]
tests/unit/test_models_organization.py::TestDocumentVisibility::test_document_visibility PASSED [ 81%]
tests/unit/test_models_organization.py::TestDocumentVisibility::test_document_private_visibility PASSED [ 84%]
tests/unit/test_models_organization.py::TestDocumentVisibility::test_document_organization_relationship PASSED [ 87%]
tests/unit/test_models_organization.py::TestDocumentVisibility::test_document_default_visibility PASSED [ 90%]
tests/unit/test_models_organization.py::TestCascadeDeletes::test_organization_delete_cascades PASSED [ 93%]

========================== 33 passed in 2.45s ===========================
All tests passed!
```

## Запуск с покрытием кода

```bash
$ ./run_tests.sh coverage

Running AI-Avangard Backend Tests
========================================
Running tests with coverage report...

========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 33 items

tests/unit/test_models_organization.py .............................. [100%]

---------- coverage: platform linux, python 3.12.0-final-0 -----------
Name                                       Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------------------
app/__init__.py                                0      0      0      0   100%
app/models/__init__.py                        12      0      0      0   100%
app/models/base.py                             3      0      0      0   100%
app/models/document.py                        24      0      4      0   100%
app/models/organization.py                    25      0      4      0   100%
app/models/organization_invite.py             21      0      4      0   100%
app/models/organization_member.py             18      0      4      0   100%
app/models/organization_settings.py           28      0      4      0   100%
app/models/user.py                            31      0      4      0   100%
---------------------------------------------------------------------------------------
TOTAL                                        162      0     24      0   100%

Coverage report generated in htmlcov/index.html

========================== 33 passed in 2.67s ===========================
All tests passed!
```

## Запуск конкретного теста (verbose)

```bash
$ pytest tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization -vv

========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 1 item

tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization PASSED [100%]

========================== 1 passed in 0.34s ============================
```

## Запуск класса тестов

```bash
$ pytest tests/unit/test_models_organization.py::TestOrganizationSettingsModel -v

========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 7 items

tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_organization_settings_defaults PASSED [ 14%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_llm_configuration PASSED [ 28%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_jsonb_fields PASSED [ 42%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_document_processing PASSED [ 57%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_language_configuration PASSED [ 71%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_citation_configuration PASSED [ 85%]
tests/unit/test_models_organization.py::TestOrganizationSettingsModel::test_settings_relationship PASSED [100%]

========================== 7 passed in 0.89s ============================
```

## Пример неуспешного теста

```bash
========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /home/temrjan/ai-avangard/backend
configfile: pytest.ini
plugins: asyncio-0.25.0, cov-6.0.0
collected 1 item

tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_unique_slug FAILED [100%]

=============================== FAILURES ================================
_____________ TestOrganizationModel.test_organization_unique_slug _______

self = <test_models_organization.TestOrganizationModel object at 0x7f8b9c123d50>
db_session = <sqlalchemy.ext.asyncio.AsyncSession object at 0x7f8b9c123e10>
test_user = <User(id=1, email=test@example.com, status=UserStatus.APPROVED)>

    @pytest.mark.asyncio
    async def test_organization_unique_slug(self, db_session: AsyncSession, test_user: User):
        """Test that slug must be unique."""
        org1 = Organization(
            name="Org One",
            slug="same-slug",
            owner_id=test_user.id
        )
        db_session.add(org1)
        await db_session.commit()

        org2 = Organization(
            name="Org Two",
            slug="same-slug",
            owner_id=test_user.id
        )
        db_session.add(org2)

>       with pytest.raises(IntegrityError):
E       Failed: DID NOT RAISE <class 'sqlalchemy.exc.IntegrityError'>

tests/unit/test_models_organization.py:123: Failed
========================== short test summary info ======================
FAILED tests/unit/test_models_organization.py::TestOrganizationModel::test_organization_unique_slug - Failed: DID NOT RAISE <class 'sqlalchemy.exc.IntegrityError'>
========================== 1 failed in 0.45s ============================
```

## Сводная статистика

```bash
$ pytest tests/unit/ --co -q

test_models_organization.py::TestOrganizationModel::test_create_organization
test_models_organization.py::TestOrganizationModel::test_organization_required_fields
test_models_organization.py::TestOrganizationModel::test_organization_unique_slug
test_models_organization.py::TestOrganizationModel::test_organization_relationships
test_models_organization.py::TestOrganizationModel::test_organization_status_enum
test_models_organization.py::TestOrganizationModel::test_organization_custom_quotas
test_models_organization.py::TestOrganizationInviteModel::test_create_invite
test_models_organization.py::TestOrganizationInviteModel::test_invite_unique_code
test_models_organization.py::TestOrganizationInviteModel::test_invite_validation
test_models_organization.py::TestOrganizationInviteModel::test_invite_expiration
test_models_organization.py::TestOrganizationInviteModel::test_invite_status_changes
test_models_organization.py::TestOrganizationInviteModel::test_invite_relationships
test_models_organization.py::TestOrganizationMemberModel::test_organization_member_history
test_models_organization.py::TestOrganizationMemberModel::test_member_with_inviter
test_models_organization.py::TestOrganizationMemberModel::test_member_leave_organization
test_models_organization.py::TestOrganizationMemberModel::test_member_role_types
test_models_organization.py::TestOrganizationSettingsModel::test_organization_settings_defaults
test_models_organization.py::TestOrganizationSettingsModel::test_settings_llm_configuration
test_models_organization.py::TestOrganizationSettingsModel::test_settings_jsonb_fields
test_models_organization.py::TestOrganizationSettingsModel::test_settings_document_processing
test_models_organization.py::TestOrganizationSettingsModel::test_settings_language_configuration
test_models_organization.py::TestOrganizationSettingsModel::test_settings_citation_configuration
test_models_organization.py::TestOrganizationSettingsModel::test_settings_relationship
test_models_organization.py::TestUserOrganizationFields::test_user_organization_fields
test_models_organization.py::TestUserOrganizationFields::test_user_platform_admin
test_models_organization.py::TestUserOrganizationFields::test_user_without_organization
test_models_organization.py::TestDocumentVisibility::test_document_visibility
test_models_organization.py::TestDocumentVisibility::test_document_private_visibility
test_models_organization.py::TestDocumentVisibility::test_document_organization_relationship
test_models_organization.py::TestDocumentVisibility::test_document_default_visibility
test_models_organization.py::TestCascadeDeletes::test_organization_delete_cascades

33 tests in 1 file
```

## Markers

```bash
$ pytest --markers

@pytest.mark.unit: Unit tests

@pytest.mark.integration: Integration tests

@pytest.mark.asyncio: Async tests

@pytest.mark.filterwarnings(warning): add a warning filter to the given test. see https://docs.pytest.org/en/stable/how-to/capture-warnings.html#pytest-mark-filterwarnings

@pytest.mark.skip(reason=None): skip the given test function with an optional reason. Example: skip(reason="no way of currently testing this") skips the test.

@pytest.mark.skipif(condition, ..., *, reason=...): skip the given test function if any of the conditions evaluate to True. Example: skipif(sys.platform == 'win32', reason="does not run on windows") skips the test if we are on the win32 platform. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-skipif

@pytest.mark.xfail(condition, ..., *, reason=..., run=True, raises=None, strict=xfail_strict): mark the test function as an expected failure if any of the conditions evaluate to True. Optionally specify a reason for better reporting and run=False if you don't even want to execute the test function. If only specific exception(s) are expected, you can list them in raises, and if the test fails in other ways, it will be reported as a true failure. See https://docs.pytest.org/en/stable/reference/reference.html#pytest-mark-xfail

@pytest.mark.parametrize(argnames, argvalues): call a test function multiple times passing in different arguments in turn. argvalues generally needs to be a list of values if argnames specifies only one name or a list of tuples of values if argnames specifies multiple names. Example: @parametrize('arg1', [1,2]) would lead to two calls of the decorated test function, one with arg1=1 and another with arg1=2.See https://docs.pytest.org/en/stable/how-to/parametrize.html for more info and examples.

@pytest.mark.usefixtures(fixturename1, fixturename2, ...): mark tests as needing all of the specified fixtures. see https://docs.pytest.org/en/stable/explanation/fixtures.html#usefixtures

@pytest.mark.tryfirst: mark a hook implementation function such that the plugin machinery will try to call it first/as early as possible. DEPRECATED, use @pytest.hookimpl(tryfirst=True) instead.

@pytest.mark.trylast: mark a hook implementation function such that the plugin machinery will try to call it last/as late as possible. DEPRECATED, use @pytest.hookimpl(trylast=True) instead.
```
