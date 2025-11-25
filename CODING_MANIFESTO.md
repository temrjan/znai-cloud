# Coding Manifesto — AI-Avangard (Znai.cloud)

**Версия:** 1.0
**Дата:** 25 ноября 2025
**Стек:** Python + FastAPI, React + TypeScript

---

## Содержание

1. [Философия](#философия)
2. [Стиль кода Python](#стиль-кода-python)
3. [Стиль кода TypeScript/React](#стиль-кода-typescriptreact)
4. [Архитектура](#архитектура)
5. [Тестирование](#тестирование)
6. [Git Workflow](#git-workflow)
7. [Code Review](#code-review)
8. [Безопасность](#безопасность)

---

## Философия

### Основные принципы

1. **Простота важнее гибкости**
   - Не создавай абстракции "на будущее"
   - Три одинаковых строки лучше преждевременной функции
   - Решай текущую задачу, не гипотетические

2. **Читаемость важнее краткости**
   - Код читают чаще, чем пишут
   - Явное лучше неявного
   - Комментируй "почему", а не "что"

3. **Работающий код важнее идеального**
   - Сначала заставь работать, потом улучшай
   - Рефакторинг — отдельная задача
   - MVP → итерации

4. **Консистентность важнее личных предпочтений**
   - Следуй существующим паттернам в проекте
   - Не меняй стиль в чужом коде без причины
   - Один способ делать одну вещь

---

## Стиль кода Python

### Форматирование

Используем **Black** + **Ruff** для автоформатирования.

```bash
# Установка
pip install black ruff

# Форматирование
black .
ruff check --fix .
```

### Конфигурация (pyproject.toml)

```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # line too long (black handles this)
```

### Именование

```python
# Переменные и функции — snake_case
user_name = "John"
def get_user_by_id(user_id: int) -> User:
    ...

# Классы — PascalCase
class UserService:
    ...

# Константы — UPPER_SNAKE_CASE
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_PAGE_SIZE = 20

# Приватные методы — с underscore
def _validate_email(email: str) -> bool:
    ...

# Boolean переменные — is_, has_, can_
is_active = True
has_permission = False
can_edit = True
```

### Type Hints

**Обязательны** для публичных функций и методов:

```python
# Хорошо
async def create_user(
    email: str,
    password: str,
    role: UserRole = UserRole.USER
) -> User:
    ...

# Сложные типы
from typing import Optional, List

async def get_documents(
    user_id: int,
    limit: Optional[int] = None
) -> List[Document]:
    ...

# Плохо — нет типов
async def create_user(email, password, role=None):
    ...
```

### Импорты

Порядок (Ruff сортирует автоматически):

```python
# 1. Стандартная библиотека
import os
from datetime import datetime
from typing import Optional, List

# 2. Сторонние пакеты
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Локальные модули
from app.core.config import settings
from app.models.user import User
from app.services.user_service import UserService
```

**Запрещено:**
```python
# Импорты внутри функций (кроме циклических зависимостей)
def some_function():
    from app.services import SomeService  # Плохо
    ...

# import *
from app.models import *
```

### Структура функций

```python
async def process_document(
    document_id: int,
    user: User,
    db: AsyncSession
) -> ProcessingResult:
    """
    Обрабатывает документ и возвращает результат.

    Args:
        document_id: ID документа для обработки
        user: Пользователь, запросивший обработку
        db: Сессия базы данных

    Returns:
        ProcessingResult с результатами обработки

    Raises:
        DocumentNotFoundError: Документ не найден
        PermissionDeniedError: Нет прав на обработку
    """
    # 1. Валидация входных данных
    document = await get_document(db, document_id)
    if not document:
        raise DocumentNotFoundError(document_id)

    # 2. Проверка прав
    if not can_process(user, document):
        raise PermissionDeniedError()

    # 3. Основная логика
    result = await _do_processing(document)

    # 4. Возврат результата
    return result
```

### Обработка ошибок

```python
# Кастомные исключения для бизнес-логики
class DocumentNotFoundError(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(f"Document {document_id} not found")

# HTTP исключения в роутах
@router.get("/{document_id}")
async def get_document(document_id: int):
    document = await document_service.get(document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    return document

# Не глотай исключения
try:
    result = await process()
except Exception:
    pass  # Плохо!

# Логируй и пробрасывай
try:
    result = await process()
except Exception as e:
    logger.error(f"Processing failed: {e}")
    raise
```

---

## Стиль кода TypeScript/React

### Форматирование

Используем **ESLint** + **Prettier**.

```bash
npm run lint
npm run format
```

### Именование

```typescript
// Переменные и функции — camelCase
const userName = "John";
function getUserById(userId: number): User { ... }

// Компоненты и типы — PascalCase
const UserProfile: React.FC<UserProfileProps> = () => { ... };
interface UserProfileProps { ... }
type UserRole = "admin" | "user";

// Константы — UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Boolean — is, has, can, should
const isLoading = true;
const hasPermission = false;
```

### Компоненты React

```typescript
// Функциональные компоненты с типами
interface ChatMessageProps {
  message: Message;
  isOwn: boolean;
  onDelete?: (id: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isOwn,
  onDelete,
}) => {
  // Хуки в начале
  const [isEditing, setIsEditing] = useState(false);
  const theme = useTheme();

  // Обработчики
  const handleDelete = useCallback(() => {
    onDelete?.(message.id);
  }, [message.id, onDelete]);

  // Early returns для условий
  if (!message.content) {
    return null;
  }

  // JSX
  return (
    <Box sx={{ ... }}>
      {message.content}
    </Box>
  );
};
```

### Хуки

```typescript
// Кастомные хуки с префиксом use
export function useDocuments(organizationId?: number) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getDocuments(organizationId);
      setDocuments(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }, [organizationId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return { documents, isLoading, error, refetch: fetchDocuments };
}
```

---

## Архитектура

### Backend — Слоистая архитектура

```
backend/app/
├── routes/          # HTTP handlers (тонкие, только валидация и ответы)
├── services/        # Бизнес-логика
├── models/          # SQLAlchemy модели
├── schemas/         # Pydantic схемы (request/response)
├── core/            # Конфигурация, безопасность
└── utils/           # Утилиты
```

**Правила:**
- Routes вызывают Services, не наоборот
- Services не знают про HTTP (никаких HTTPException)
- Models только для БД, Schemas для API
- Один файл < 300 строк (иначе — разделять)

### Frontend — Feature-based структура

```
frontend/src/
├── components/      # Переиспользуемые компоненты
├── pages/           # Страницы (роуты)
├── hooks/           # Кастомные хуки
├── services/        # API вызовы
├── types/           # TypeScript типы
└── utils/           # Утилиты
```

---

## Тестирование

### Философия тестирования

1. **Тестируй поведение, не реализацию**
2. **Один тест — одна проверка**
3. **Тесты должны быть быстрыми**
4. **Тесты должны быть независимыми**

### Виды тестов

| Тип | Что тестирует | Coverage цель |
|-----|---------------|---------------|
| Unit | Отдельные функции/классы | 70%+ |
| Integration | Взаимодействие компонентов | Критичные пути |
| E2E | Весь flow от UI до БД | Основные сценарии |

### Структура теста (AAA)

```python
# Arrange-Act-Assert
async def test_create_user_success():
    # Arrange — подготовка
    user_data = UserCreate(
        email="test@example.com",
        password="securepass123"
    )

    # Act — действие
    user = await user_service.create(user_data)

    # Assert — проверка
    assert user.email == "test@example.com"
    assert user.id is not None
    assert user.is_active is True
```

### Именование тестов

```python
# Формат: test_<что_тестируем>_<условие>_<ожидаемый_результат>

# Хорошо
def test_create_user_with_valid_data_returns_user():
def test_create_user_with_existing_email_raises_error():
def test_login_with_wrong_password_returns_401():

# Плохо
def test_user():
def test_create():
def test_1():
```

### Запуск тестов

```bash
# Все тесты
pytest

# С coverage
pytest --cov=app --cov-report=html

# Конкретный файл
pytest tests/test_user_service.py

# Конкретный тест
pytest tests/test_user_service.py::test_create_user_success

# Только быстрые (без БД)
pytest -m "not integration"
```

### Минимальный coverage

- **Новый код:** 80%+
- **Services:** 70%+
- **Routes:** 50%+ (интеграционные тесты)
- **Utils:** 90%+

---

## Git Workflow

### Ветки

```
main              # Production (защищённая)
├── develop       # Staging/интеграция
    ├── feature/  # Новые фичи
    ├── fix/      # Исправления багов
    └── refactor/ # Рефакторинг
```

### Именование веток

```bash
# Формат: <тип>/<краткое-описание>

feature/user-authentication
feature/document-upload
fix/hybrid-search-bug
fix/login-validation
refactor/split-organizations
```

### Коммиты

Формат: **Conventional Commits**

```
<тип>(<область>): <описание>

# Типы:
feat     # Новая функциональность
fix      # Исправление бага
refactor # Рефакторинг без изменения поведения
docs     # Документация
test     # Тесты
chore    # Настройка, зависимости

# Примеры:
feat(auth): add password reset functionality
fix(search): fix hybrid search for personal documents
refactor(org): extract OrganizationService
docs(api): update API documentation
test(user): add unit tests for UserService
chore(deps): update FastAPI to 0.109.0
```

### Pull Request

1. **Название:** Как коммит (feat(auth): add login)
2. **Описание:** Что сделано и зачем
3. **Размер:** < 400 строк изменений (иначе разбить)
4. **Тесты:** Покрыть изменения
5. **Review:** Минимум 1 approve

### Запрещено

- Push напрямую в main
- Force push в общие ветки
- Merge без review
- Коммиты типа "fix", "update", "wip"

---

## Code Review

### Чек-лист для автора

- [ ] Код работает локально
- [ ] Тесты проходят
- [ ] Линтеры не ругаются
- [ ] Нет console.log / print для дебага
- [ ] Нет захардкоженных значений
- [ ] Нет секретов в коде
- [ ] PR < 400 строк

### Чек-лист для ревьюера

- [ ] Код понятен без объяснений
- [ ] Нет очевидных багов
- [ ] Обработка ошибок адекватная
- [ ] Нет проблем с безопасностью
- [ ] Тесты покрывают изменения
- [ ] Нет дублирования кода
- [ ] Именование понятное

### Тон комментариев

```
# Хорошо — конструктивно
"Можно упростить, используя list comprehension"
"Здесь возможен None, стоит добавить проверку"
"Этот паттерн уже есть в utils/helpers.py"

# Плохо — токсично
"Это неправильно"
"Зачем так делать?"
"Очевидно же, что..."
```

---

## Безопасность

### Обязательные правила

1. **Никаких секретов в коде**
   ```python
   # Плохо
   API_KEY = "sk-1234567890"

   # Хорошо
   API_KEY = os.getenv("API_KEY")
   ```

2. **Валидация входных данных**
   ```python
   # Pydantic валидирует автоматически
   class UserCreate(BaseModel):
       email: EmailStr
       password: str = Field(min_length=8)
   ```

3. **Параметризованные SQL запросы**
   ```python
   # SQL injection
   query = f"SELECT * FROM users WHERE id = {user_id}"

   # Безопасно
   query = select(User).where(User.id == user_id)
   ```

4. **Проверка прав доступа**
   ```python
   # Всегда проверяй, что пользователь имеет доступ к ресурсу
   if document.user_id != current_user.id:
       raise HTTPException(status_code=403)
   ```

5. **Rate Limiting на критичных endpoints**
   - /auth/login
   - /auth/register
   - /chat (дорогие AI запросы)

---

## Инструменты

### Обязательные

| Инструмент | Назначение | Команда |
|------------|------------|---------|
| Black | Форматирование Python | `black .` |
| Ruff | Линтинг Python | `ruff check .` |
| ESLint | Линтинг TypeScript | `npm run lint` |
| Prettier | Форматирование JS/TS | `npm run format` |
| pytest | Тестирование Python | `pytest` |
| mypy | Проверка типов Python | `mypy app/` |

### Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Установка:
```bash
pip install pre-commit
pre-commit install
```

---

## Итого

1. **Пиши простой, читаемый код**
2. **Следуй существующим паттернам**
3. **Покрывай тестами**
4. **Делай маленькие PR**
5. **Будь конструктивен на review**
6. **Думай о безопасности**

---

*Этот документ — живой. Обновляй по мере роста команды и проекта.*
