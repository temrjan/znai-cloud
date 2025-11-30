# Testing Guide for AI-Avangard Backend

Полное руководство по тестированию backend приложения AI-Avangard.

## Быстрый старт

### 1. Установка зависимостей

```bash
cd /home/temrjan/znai-cloud/backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Запуск тестов

```bash
# Все тесты
./run_tests.sh

# Только unit тесты
./run_tests.sh unit

# Только тесты моделей организаций
./run_tests.sh models

# С отчетом о покрытии
./run_tests.sh coverage
```

## Структура тестов

```
backend/tests/
├── __init__.py
├── conftest.py                     # Общие fixtures
├── README.md                       # Документация тестов
├── TESTING_GUIDE.md               # Это руководство
├── unit/
│   ├── __init__.py
│   └── test_models_organization.py  # Тесты моделей организаций
└── integration/
    └── __init__.py
```

## Unit тесты организаций

Файл: `/home/temrjan/znai-cloud/backend/tests/unit/test_models_organization.py`

### Что тестируется

#### 1. Organization Model (TestOrganizationModel)

**test_create_organization** - Создание организации
```python
# Проверяет:
- Создание с обязательными полями (name, slug, owner_id)
- Дефолтные значения:
  * max_members = 10
  * max_documents = 50
  * max_storage_mb = 1000
  * max_queries_per_user_daily = 100
  * max_queries_org_daily = 500
  * status = ACTIVE
- Автоматические поля (id, created_at)
```

**test_organization_required_fields** - Обязательные поля
```python
# Проверяет, что нельзя создать организацию без:
- name
- slug
- owner_id
```

**test_organization_unique_slug** - Уникальность slug
```python
# Проверяет, что slug должен быть уникальным
# Ожидается IntegrityError при дубликате
```

**test_organization_relationships** - Связи
```python
# Проверяет:
- owner relationship (ForeignKey к User)
- members relationship (обратная связь через User.organization_id)
```

**test_organization_status_enum** - Статусы
```python
# Проверяет переходы между статусами:
- ACTIVE (по умолчанию)
- SUSPENDED
- DELETED (с deleted_at)
```

**test_organization_custom_quotas** - Кастомные квоты
```python
# Проверяет установку нестандартных значений квот
```

#### 2. OrganizationInvite Model (TestOrganizationInviteModel)

**test_create_invite** - Создание инвайта
```python
# Проверяет:
- Автоматическая генерация UUID code
- Дефолтные значения:
  * max_uses = None (неограниченно)
  * used_count = 0
  * default_role = "member"
  * status = ACTIVE
```

**test_invite_unique_code** - Уникальность кодов
```python
# Проверяет, что каждый инвайт получает уникальный UUID
```

**test_invite_validation** - Валидация использования
```python
# Проверяет логику:
- used_count <= max_uses
- Симулирует использование инвайта
```

**test_invite_expiration** - Истечение срока
```python
# Проверяет:
- Установку expires_at
- Сравнение с текущим временем
```

**test_invite_status_changes** - Изменение статусов
```python
# Проверяет переходы:
- ACTIVE -> REVOKED
- ACTIVE -> EXPIRED
```

**test_invite_relationships** - Связи
```python
# Проверяет:
- organization relationship
- created_by relationship
```

#### 3. OrganizationMember Model (TestOrganizationMemberModel)

**test_organization_member_history** - История членства
```python
# Проверяет:
- Создание записи о членстве
- Поля: organization_id, user_id, role, joined_at
- left_at = None для активных членов
```

**test_member_with_inviter** - Информация о пригласившем
```python
# Проверяет:
- invited_by_user_id
- invited_by relationship
```

**test_member_leave_organization** - Выход из организации
```python
# Проверяет:
- Установку left_at
- left_at >= joined_at
```

**test_member_role_types** - Типы ролей
```python
# Проверяет различные роли:
- owner
- admin
- member
- viewer
```

#### 4. OrganizationSettings Model (TestOrganizationSettingsModel)

**test_organization_settings_defaults** - Дефолтные настройки
```python
# Проверяет все поля по умолчанию:
- LLM: custom_temperature, custom_max_tokens, etc = None
- Language: require_bilingual_response = False
- Response: include_sources_inline = True
- Response: show_confidence_score = False
```

**test_settings_llm_configuration** - Настройки LLM
```python
# Проверяет:
- custom_system_prompt
- custom_temperature (0.7)
- custom_max_tokens (2000)
- custom_model ("gpt-4")
```

**test_settings_jsonb_fields** - JSONB поля
```python
# Проверяет сложные JSON данные:
- custom_terminology: {"продукт": "изделие"}
- content_filters: {"blocked_words": [...], "min_confidence": 0.8}
- secondary_languages: {"languages": ["en", "kk"]}
```

**test_settings_document_processing** - Обработка документов
```python
# Проверяет:
- chunk_size = 512
- chunk_overlap = 50
```

**test_settings_language_configuration** - Языковые настройки
```python
# Проверяет:
- primary_language = "ru"
- require_bilingual_response = True
```

**test_settings_citation_configuration** - Настройки цитирования
```python
# Проверяет:
- citation_format = "inline"
- citation_template = "[{source}] ({confidence})"
- include_sources_inline = True
- show_confidence_score = True
```

#### 5. User Organization Fields (TestUserOrganizationFields)

**test_user_organization_fields** - Поля организации в User
```python
# Проверяет новые поля:
- organization_id
- role_in_org
- is_platform_admin
```

**test_user_platform_admin** - Платформенный админ
```python
# Проверяет:
- is_platform_admin = True
- organization_id = None (не привязан к организации)
```

**test_user_without_organization** - Пользователь без организации
```python
# Проверяет:
- organization_id = None
- role_in_org = None
- is_platform_admin = False (по умолчанию)
```

#### 6. Document Visibility (TestDocumentVisibility)

**test_document_visibility** - Видимость документов
```python
# Проверяет:
- visibility field
- organization_id
- uploaded_by_user_id
```

**test_document_private_visibility** - Приватные документы
```python
# Проверяет:
- visibility = "private"
- organization_id = None
```

**test_document_organization_relationship** - Связи документов
```python
# Проверяет:
- uploaded_by_user relationship
- organization relationship
```

**test_document_default_visibility** - Дефолтная видимость
```python
# Проверяет:
- visibility = "private" по умолчанию
```

#### 7. Cascade Deletes (TestCascadeDeletes)

**test_organization_delete_cascades** - Каскадное удаление
```python
# Проверяет удаление при удалении организации:
- OrganizationSettings (CASCADE)
- OrganizationInvite (CASCADE)
- OrganizationMember (CASCADE)
```

## Используемые технологии

### Pytest
- **pytest-asyncio**: Для асинхронных тестов
- **pytest-cov**: Для отчетов о покрытии кода
- **pytest-mock**: Для моков (если потребуется)

### База данных для тестов
- **SQLite in-memory**: Быстрая, изолированная база для каждого теста
- **aiosqlite**: Async драйвер для SQLite

### Фикстуры

#### engine (из conftest.py)
```python
@pytest.fixture
async def engine():
    """Создает новый engine для каждого теста"""
    # Создает таблицы
    # Возвращает engine
    # Удаляет таблицы после теста
```

#### db_session (из conftest.py)
```python
@pytest.fixture
async def db_session(engine):
    """Создает session с автоматическим rollback"""
    # Создает session
    # Возвращает session
    # Делает rollback после теста
```

#### test_user (из test_models_organization.py)
```python
@pytest.fixture
async def test_user(db_session):
    """Создает тестового пользователя"""
    # email: test@example.com
    # status: APPROVED
    # role: USER
```

#### test_organization (из test_models_organization.py)
```python
@pytest.fixture
async def test_organization(db_session, test_user):
    """Создает тестовую организацию"""
    # name: Test Organization
    # slug: test-org
    # owner: test_user
```

## Примеры запуска

### Один тест
```bash
cd /home/temrjan/znai-cloud/backend
pytest tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization -v
```

### Класс тестов
```bash
pytest tests/unit/test_models_organization.py::TestOrganizationInviteModel -v
```

### С выводом print
```bash
pytest tests/unit/test_models_organization.py -s
```

### С покрытием
```bash
pytest tests/unit/test_models_organization.py --cov=app.models --cov-report=term-missing
```

### Только failed тесты
```bash
pytest --lf  # last failed
pytest --ff  # failed first
```

## Отладка тестов

### Использование pdb
```python
@pytest.mark.asyncio
async def test_something(db_session):
    import pdb; pdb.set_trace()  # Точка останова
    # или
    breakpoint()  # Python 3.7+
```

### Verbose вывод
```bash
pytest -vv  # Very verbose
pytest -vv -s  # С print statements
```

### Логирование
```python
import logging
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.asyncio
async def test_something(db_session):
    logging.debug("Debug message")
```

## Best Practices

1. **Изоляция**: Каждый тест независим
2. **Naming**: Понятные имена тестов
3. **AAA Pattern**: Arrange, Act, Assert
4. **Async**: Всегда `@pytest.mark.asyncio` для async функций
5. **Cleanup**: Фикстуры автоматически очищают данные
6. **Coverage**: Стремимся к 80%+ покрытию

## Troubleshooting

### ModuleNotFoundError: No module named 'backend'

**Решение 1**: Запускать из директории backend
```bash
cd /home/temrjan/znai-cloud/backend
pytest
```

**Решение 2**: Добавить в PYTHONPATH
```bash
export PYTHONPATH=/home/temrjan/znai-cloud/backend:$PYTHONPATH
pytest
```

### IntegrityError в тестах

**Причина**: Нарушение constraints (unique, foreign key)

**Решение**: Проверить, что:
1. Используется свежая сессия через фикстуру
2. Данные уникальны (или используется rollback)
3. Foreign keys существуют

### Async warnings

**Причина**: Неправильная настройка asyncio

**Решение**: Проверить pytest.ini:
```ini
[pytest]
asyncio_mode = auto
```

## CI/CD Integration

Пример для GitHub Actions:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

## Дальнейшее развитие

Планируемые тесты:

1. **Integration тесты**
   - API endpoints
   - Database transactions
   - External services

2. **Performance тесты**
   - Load testing
   - Query optimization

3. **E2E тесты**
   - Full user flows
   - Multi-user scenarios

4. **Security тесты**
   - Authentication
   - Authorization
   - Input validation
