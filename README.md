# AI-Avangard - Multi-tenant RAG Platform

**Демо-платформа для создания персональных баз знаний с AI ассистентом**

---

## 📋 Обзор проекта

AI-Avangard - это SaaS платформа для создания персональных баз знаний с использованием RAG (Retrieval-Augmented Generation). Пользователи могут загружать документы, индексировать их и задавать вопросы AI ассистенту.

### Ключевые возможности

- ✅ Регистрация с подтверждением администратором
- ✅ Загрузка до 5 документов (бесплатно)
- ✅ Персональная база знаний (изолированная)
- ✅ RAG-запросы с цитированием источников
- ✅ Квоты: 5 документов, 100 запросов/день
- ✅ UI в стиле GitHub (Primer React)

### Технический стек

**Backend:**
- Python 3.12+
- FastAPI (async web framework)
- PostgreSQL 16 (пользователи, метаданные)
- Redis 7.x (кеширование, rate limiting)
- Qdrant 1.12+ (векторная БД)
- OpenAI API (embeddings + GPT-4o)
- LlamaIndex (RAG orchestration)

**Frontend:**
- React 18 + TypeScript
- Vite 6 (build tool)
- Primer React (GitHub UI components)
- React Router v6
- Axios (HTTP client)

**DevOps:**
- Nginx (reverse proxy + SSL)
- systemd (process management)
- pytest (backend tests)
- vitest (frontend tests)

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Nginx (Reverse Proxy + SSL Termination)                │
│  - Static: /frontend/dist                               │
│  - API: proxy → localhost:8000                          │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  FastAPI Backend (Python)                               │
│  ├── Routes (auth, chat, documents, admin)              │
│  ├── Services (qdrant, indexing, llm)                   │
│  ├── Models (SQLAlchemy ORM)                            │
│  └── Middleware (auth, rate limiting)                   │
└──────┬──────────┬──────────┬──────────────────────────┘
       │          │          │
   ┌───▼───┐  ┌──▼───┐  ┌───▼────┐
   │ PG    │  │Redis │  │ Qdrant │
   │ SQL   │  │Cache │  │ Vector │
   │       │  │      │  │   DB   │
   └───────┘  └──────┘  └───┬────┘
                            │
                        ┌───▼────┐
                        │ OpenAI │
                        │  API   │
                        └────────┘
```

---

## 📁 Структура проекта

```
/home/temrjan/znai-cloud/
├── docs/
│   ├── ARCHITECTURE.md          # Подробная архитектура
│   ├── API.md                   # API документация
│   ├── DEPLOYMENT.md            # Инструкция по развертыванию
│   └── TESTING.md               # Руководство по тестированию
│
├── backend/
│   ├── alembic/                 # Миграции БД
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Конфигурация
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   └── quota.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   └── admin.py
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── qdrant_service.py
│   │   │   ├── indexing_service.py
│   │   │   └── llm_service.py
│   │   ├── middleware/          # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── rate_limit.py
│   │   └── utils/               # Утилиты
│   │       ├── __init__.py
│   │       ├── security.py
│   │       └── validators.py
│   ├── tests/                   # Тесты
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── unit/                # Unit tests
│   │   │   ├── test_auth.py
│   │   │   ├── test_qdrant.py
│   │   │   └── test_indexing.py
│   │   └── integration/         # Integration tests
│   │       ├── test_api.py
│   │       └── test_rag.py
│   ├── requirements.txt         # Production зависимости
│   ├── requirements-dev.txt     # Dev зависимости
│   ├── pytest.ini               # Pytest конфигурация
│   ├── alembic.ini             # Alembic конфигурация
│   └── pyproject.toml          # Python проект конфигурация
│
├── frontend/
│   ├── src/
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx    # Главный layout (GitHub-style)
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   ├── DocumentsPage.tsx
│   │   │   └── AdminPage.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx       # GitHub Header
│   │   │   ├── Sidebar.tsx      # GitHub Sidebar
│   │   │   ├── ChatMessage.tsx  # Comment-style message
│   │   │   ├── DocumentCard.tsx
│   │   │   └── QuotaBadge.tsx
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useDocuments.ts
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── formatters.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/
│   │   ├── components/
│   │   │   └── ChatMessage.test.tsx
│   │   └── setup.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── vitest.config.ts        # Vitest конфигурация
│
├── infrastructure/
│   ├── nginx/
│   │   └── znai-cloud.conf    # Nginx конфиг
│   ├── systemd/
│   │   ├── znai-cloud-backend.service
│   │   └── qdrant.service
│   └── scripts/
│       ├── setup.sh            # Автоматическая установка
│       └── backup.sh           # Бэкап скрипт
│
├── data/
│   ├── users/                  # Файлы пользователей
│   │   ├── 1/
│   │   ├── 2/
│   │   └── ...
│   └── qdrant/                 # Qdrant данные
│
├── logs/
│   ├── backend.log
│   └── nginx/
│
├── .env.example                # Пример конфигурации
├── .env                        # Реальная конфигурация (не в git)
├── .gitignore
├── Makefile                    # Команды управления
└── README.md                   # Этот файл
```

---

## 🗄️ Схема базы данных

### PostgreSQL

```sql
-- Пользователи
users:
  id: SERIAL PRIMARY KEY
  email: VARCHAR(255) UNIQUE NOT NULL
  password_hash: VARCHAR(255) NOT NULL
  full_name: VARCHAR(255)
  status: ENUM('pending', 'approved', 'rejected') DEFAULT 'pending'
  role: ENUM('user', 'admin') DEFAULT 'user'
  approved_by: INT REFERENCES users(id)
  created_at: TIMESTAMP DEFAULT NOW()
  approved_at: TIMESTAMP

-- Квоты пользователей
user_quotas:
  user_id: INT PRIMARY KEY REFERENCES users(id)
  max_documents: INT DEFAULT 5
  current_documents: INT DEFAULT 0
  max_queries_daily: INT DEFAULT 100
  queries_today: INT DEFAULT 0
  last_query_date: DATE

-- Документы
documents:
  id: UUID PRIMARY KEY
  user_id: INT REFERENCES users(id)
  filename: VARCHAR(255) NOT NULL
  file_size: BIGINT
  file_hash: VARCHAR(64)
  chunks_count: INT DEFAULT 0
  status: ENUM('processing', 'indexed', 'failed')
  uploaded_at: TIMESTAMP DEFAULT NOW()
  indexed_at: TIMESTAMP
  UNIQUE(user_id, file_hash)

-- Лог запросов
query_logs:
  id: BIGSERIAL PRIMARY KEY
  user_id: INT REFERENCES users(id)
  query_text: TEXT
  response_time_ms: INT
  sources_count: INT
  created_at: TIMESTAMP DEFAULT NOW()
```

### Qdrant

```
Collection: ai_avangard_main
  vectors: 3072 dimensions (text-embedding-3-large)
  payload:
    - user_id: INT (indexed)
    - doc_id: UUID
    - filename: STRING
    - chunk_index: INT
    - text: STRING
    - created_at: DATETIME
```

---

## ⚙️ Конфигурация

### Системные требования

**Минимальные:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB
- OS: Ubuntu 22.04+

**Рекомендуемые (100 пользователей):**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- Bandwidth: 100 Mbps

### Переменные окружения

См. `.env.example` для полного списка конфигурации.

**Критические:**
```env
OPENAI_API_KEY=sk-proj-xxxxx
POSTGRES_PASSWORD=secure_password
JWT_SECRET_KEY=very_long_random_string
```

---

## 🚀 Быстрый старт

### 1. Клонирование (уже сделано)

```bash
cd /home/temrjan/znai-cloud
```

### 2. Установка зависимостей (следующий шаг)

```bash
# Будет выполнено автоматически
make setup
```

### 3. Конфигурация

```bash
cp .env.example .env
nano .env  # Заполнить API ключи
```

### 4. Запуск

```bash
make run
```

---

## 🧪 Тестирование

### Backend тесты

```bash
cd backend
pytest                          # Все тесты
pytest tests/unit              # Unit тесты
pytest tests/integration       # Integration тесты
pytest --cov=app               # С coverage
```

### Frontend тесты

```bash
cd frontend
npm test                       # Все тесты
npm test -- --coverage        # С coverage
```

---

## 📊 Мониторинг

**Логи:**
```bash
tail -f logs/backend.log       # Backend логи
sudo tail -f /var/log/nginx/access.log  # Nginx логи
```

**Статус сервисов:**
```bash
systemctl status znai-cloud-backend
systemctl status qdrant
systemctl status postgresql
systemctl status redis
```

**Метрики:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/admin/stats
```

---

## 🔐 Безопасность

- ✅ JWT токены (HS256)
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting (Redis)
- ✅ CORS protection
- ✅ SQL injection protection (SQLAlchemy)
- ✅ XSS protection (CSP headers)
- ✅ User data isolation (Qdrant filters)

---

## 📈 Масштабируемость

**Текущая емкость:**
- 100 пользователей
- 500 документов (100 × 5)
- ~25,000 векторов
- ~300 MB RAM для Qdrant

**Для роста:**
- Horizontal scaling: Nginx load balancer
- Database: PostgreSQL read replicas
- Cache: Redis cluster
- Vectors: Qdrant distributed mode

---

## 📝 Лицензия

Proprietary - AI-Avangard © 2025

---

## 👥 Команда

- **Tech Lead**: temrjan
- **Email**: x.temrjan@gmail.com

---

**Version**: 1.0.0
**Status**: 🚧 In Development
**Last Updated**: 2025-11-20
