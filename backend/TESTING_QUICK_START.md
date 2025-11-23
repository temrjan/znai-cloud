# Testing Quick Start

## Установка

```bash
cd /home/temrjan/ai-avangard/backend
pip install -r requirements-dev.txt
```

## Запуск тестов

### Все тесты
```bash
./run_tests.sh
```

### Только модели организаций
```bash
./run_tests.sh models
```

### Unit тесты
```bash
./run_tests.sh unit
```

### С покрытием кода
```bash
./run_tests.sh coverage
open htmlcov/index.html  # Посмотреть отчет
```

## Один тест

```bash
pytest tests/unit/test_models_organization.py::TestOrganizationModel::test_create_organization -v
```

## Документация

- **tests/README.md** - Общая документация
- **tests/TESTING_GUIDE.md** - Подробное руководство
- **tests/SUMMARY.md** - Краткое описание

## Покрытие

- Organization model - ✅
- OrganizationInvite - ✅
- OrganizationMember - ✅
- OrganizationSettings - ✅
- User (org fields) - ✅
- Document (visibility) - ✅
- Cascade deletes - ✅

**Всего**: 33+ тестов, 783 строки кода
