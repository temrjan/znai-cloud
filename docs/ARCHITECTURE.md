# Архитектура AI-Avangard

## 🎯 Принципы разработки

### 1. **Mobile-First Design** 🔥
**Критический приоритет**: Все компоненты разрабатываются сначала для мобильных устройств, затем адаптируются для десктопа.

**Breakpoints:**
```css
mobile:  320px - 768px   (primary target)
tablet:  768px - 1024px
desktop: 1024px+         (enhancement)
```

**Требования:**
- ✅ Touch-friendly кнопки (min 44px)
- ✅ Читаемые шрифты на малых экранах
- ✅ Hamburger menu для навигации
- ✅ Оптимизация загрузки (lazy loading)
- ✅ Тестирование на реальных устройствах

### 2. Clean Architecture
- Разделение на слои (routes → services → models)
- Dependency Injection
- Единая ответственность классов

### 3. Test-Driven Development
- Unit tests: 80%+ coverage
- Integration tests для критических путей
- E2E tests для основных сценариев

### 4. Безопасность
- Zero-trust: проверка на каждом уровне
- Изоляция данных пользователей
- Rate limiting

---

## 🏗️ Архитектура Backend

### Структура слоев

```
┌─────────────────────────────────────┐
│     Routes (API Endpoints)          │  ← HTTP handlers
├─────────────────────────────────────┤
│     Middleware (Auth, RateLimit)    │  ← Cross-cutting concerns
├─────────────────────────────────────┤
│     Services (Business Logic)       │  ← Core logic
├─────────────────────────────────────┤
│     Models (Data Layer)             │  ← Database ORM
└─────────────────────────────────────┘
```

### Компоненты

#### 1. Routes (API Layer)
**Responsibility**: HTTP request handling, validation, response formatting

```python
# backend/app/routes/chat.py
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: User = Depends(get_current_user)
):
    """
    RAG chat endpoint
    - Validates request
    - Delegates to ChatService
    - Returns formatted response
    """
    return await chat_service.process_query(user.id, request.message)
```

#### 2. Services (Business Logic Layer)
**Responsibility**: Core business logic, orchestration

```python
# backend/app/services/chat_service.py
class ChatService:
    def __init__(
        self,
        qdrant: QdrantService,
        llm: LLMService,
        quota: QuotaService
    ):
        self.qdrant = qdrant
        self.llm = llm
        self.quota = quota

    async def process_query(self, user_id: int, query: str):
        # 1. Check quota
        await self.quota.check_and_increment(user_id)

        # 2. Search vectors (with user isolation)
        results = await self.qdrant.search(
            query=query,
            filter={"user_id": user_id}
        )

        # 3. Generate answer
        answer = await self.llm.generate(
            context=[r.text for r in results],
            question=query
        )

        return ChatResponse(answer=answer, sources=results)
```

#### 3. Models (Data Layer)
**Responsibility**: Database schema, ORM

```python
# backend/app/models/user.py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)

    # Relationships
    quota = relationship("UserQuota", back_populates="user", uselist=False)
    documents = relationship("Document", back_populates="user")
```

### Dependency Injection

```python
# backend/app/dependencies.py
def get_qdrant_service() -> QdrantService:
    return QdrantService(
        client=qdrant_client,
        collection_name=settings.QDRANT_COLLECTION
    )

def get_chat_service(
    qdrant: QdrantService = Depends(get_qdrant_service),
    llm: LLMService = Depends(get_llm_service)
) -> ChatService:
    return ChatService(qdrant=qdrant, llm=llm)
```

---

## 🎨 Архитектура Frontend (Mobile-First)

### Component Hierarchy

```
App
├── ThemeProvider (Primer)
├── AuthProvider (Context)
└── AppLayout
    ├── Header (fixed, mobile-friendly)
    │   ├── Logo
    │   ├── HamburgerMenu (mobile)
    │   └── UserMenu
    ├── Sidebar (collapsible)
    │   ├── NavList
    │   └── QuotaBadge
    └── PageContent (responsive)
        ├── ChatPage
        ├── DocumentsPage
        └── AdminPage
```

### Mobile-First CSS Strategy

```typescript
// frontend/src/styles/responsive.ts
export const breakpoints = {
  mobile: '320px',
  tablet: '768px',
  desktop: '1024px'
}

// Mobile-first media queries
export const media = {
  tablet: `@media (min-width: ${breakpoints.tablet})`,
  desktop: `@media (min-width: ${breakpoints.desktop})`
}

// Usage:
const Container = styled(Box)`
  /* Mobile (default) */
  padding: 12px;
  font-size: 14px;

  /* Tablet */
  ${media.tablet} {
    padding: 16px;
    font-size: 16px;
  }

  /* Desktop */
  ${media.desktop} {
    padding: 24px;
    max-width: 1200px;
  }
`
```

### Primer React Responsive Components

```typescript
// Primer автоматически адаптивен
<PageLayout>
  {/* Sidebar скрывается на mobile */}
  <PageLayout.Pane
    position="start"
    hidden={{ narrow: true }}  // ← скрыт на mobile
  >
    <Sidebar />
  </PageLayout.Pane>

  {/* Content адаптируется */}
  <PageLayout.Content>
    <Chat />
  </PageLayout.Content>
</PageLayout>

// Responsive Header
<Header>
  {/* Mobile: HamburgerMenu */}
  <Header.Item sx={{ display: ['block', 'none'] }}>
    <IconButton icon={ThreeBarsIcon} />
  </Header.Item>

  {/* Desktop: Full nav */}
  <Header.Item sx={{ display: ['none', 'block'] }}>
    <NavList />
  </Header.Item>
</Header>
```

### Touch-Friendly UI

```typescript
// Минимальные размеры для touch
const TOUCH_TARGET_SIZE = 44; // px (Apple HIG)

<Button
  sx={{
    minWidth: TOUCH_TARGET_SIZE,
    minHeight: TOUCH_TARGET_SIZE,
    fontSize: ['14px', '16px'] // mobile, desktop
  }}
>
  Send
</Button>
```

---

## 🔐 Безопасность: Multi-Tenancy Isolation

### Изоляция данных

**Уровень 1: Middleware**
```python
@app.middleware("http")
async def enforce_user_context(request: Request, call_next):
    # Извлекаем user_id из JWT
    user_id = get_user_id_from_token(request)

    # Добавляем в request state
    request.state.user_id = user_id

    return await call_next(request)
```

**Уровень 2: Service Layer**
```python
class QdrantService:
    async def search(self, query: str, user_id: int):
        # ОБЯЗАТЕЛЬНАЯ фильтрация
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=user_id)
                )
            ]
        )

        return await self.client.search(
            collection_name=self.collection,
            query_vector=embed(query),
            query_filter=filter_condition  # ← ИЗОЛЯЦИЯ
        )
```

**Уровень 3: Database**
```sql
-- Row-Level Security (PostgreSQL)
CREATE POLICY user_documents_policy ON documents
    USING (user_id = current_setting('app.current_user_id')::int);
```

---

## 📊 Data Flow

### Запрос к RAG (User Query)

```
┌─────────────┐
│ User (mobile│
│  browser)   │
└──────┬──────┘
       │ POST /chat {message}
       ▼
┌─────────────────────────────┐
│ Nginx (SSL termination)     │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ FastAPI Middleware          │
│ - Extract JWT               │
│ - Validate user_id          │
│ - Rate limiting check       │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ ChatService                 │
│ 1. Check quota              │
│ 2. Search Qdrant (filtered) │
│ 3. Generate answer (OpenAI) │
│ 4. Log query                │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Response (JSON)             │
│ {                           │
│   answer: "...",            │
│   sources: [...],           │
│   quota: {used: 15, limit: 100} │
│ }                           │
└─────────────────────────────┘
```

### Загрузка документа (Upload Flow)

```
User uploads file (mobile)
    ↓
Frontend: Validate (size, type)
    ↓
POST /documents/upload
    ↓
Backend:
    1. Check quota (5/5?)
    2. Save file → /data/users/{user_id}/
    3. Calculate hash (deduplication)
    4. Split into chunks
    5. Generate embeddings (OpenAI)
    6. Store in Qdrant (with user_id)
    7. Update PostgreSQL
    8. Increment quota
    ↓
Response: {doc_id, chunks_count, quota}
```

---

## 🧪 Тестирование

### Backend Test Strategy

**1. Unit Tests (80%+ coverage)**
```python
# tests/unit/test_chat_service.py
@pytest.mark.asyncio
async def test_chat_service_enforces_user_isolation(mock_qdrant):
    service = ChatService(qdrant=mock_qdrant, llm=mock_llm)

    await service.process_query(user_id=1, query="test")

    # Проверяем что фильтр применён
    mock_qdrant.search.assert_called_once()
    call_args = mock_qdrant.search.call_args
    assert call_args.kwargs['filter']['must'][0]['key'] == 'user_id'
    assert call_args.kwargs['filter']['must'][0]['match']['value'] == 1
```

**2. Integration Tests**
```python
# tests/integration/test_rag_flow.py
async def test_full_rag_flow(client, test_user, test_document):
    # 1. Upload document
    response = await client.post(
        "/documents/upload",
        files={"file": test_document},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200

    # 2. Wait for indexing
    await asyncio.sleep(2)

    # 3. Query RAG
    response = await client.post(
        "/chat",
        json={"message": "test query"},
        headers={"Authorization": f"Bearer {test_user.token}"}
    )

    assert response.status_code == 200
    assert "answer" in response.json()
```

### Frontend Test Strategy

**1. Component Tests (Vitest + Testing Library)**
```typescript
// tests/components/ChatMessage.test.tsx
import { render, screen } from '@testing-library/react'
import { ChatMessage } from '@/components/ChatMessage'

describe('ChatMessage (Mobile)', () => {
  it('renders correctly on mobile viewport', () => {
    // Set mobile viewport
    global.innerWidth = 375

    render(<ChatMessage text="Hello" sender="user" />)

    const message = screen.getByText('Hello')
    expect(message).toBeInTheDocument()

    // Check mobile-specific styles
    expect(message).toHaveStyle({ fontSize: '14px' })
  })
})
```

**2. Responsive Tests**
```typescript
describe('AppLayout responsiveness', () => {
  it('shows hamburger menu on mobile', () => {
    render(<AppLayout />, { viewport: 'mobile' })
    expect(screen.getByLabelText('Menu')).toBeVisible()
  })

  it('shows full sidebar on desktop', () => {
    render(<AppLayout />, { viewport: 'desktop' })
    expect(screen.getByRole('navigation')).toBeVisible()
  })
})
```

---

## 📈 Performance Optimization

### Backend
- ✅ Connection pooling (PostgreSQL, Redis)
- ✅ Async I/O (asyncio, aiohttp)
- ✅ Response caching (Redis)
- ✅ Database indexing (user_id, email)

### Frontend (Mobile-First)
- ✅ Code splitting (Vite)
- ✅ Lazy loading компонентов
- ✅ Image optimization (WebP, lazy load)
- ✅ Минимизация bundle size
- ✅ Service Worker (offline support)

### Metrics
```
Target (Mobile 4G):
- First Contentful Paint: < 1.8s
- Time to Interactive: < 3.8s
- Lighthouse Score: > 90
```

---

## 🔄 CI/CD Pipeline (будущее)

```yaml
# .github/workflows/main.yml
on: [push, pull_request]

jobs:
  backend-tests:
    - Run pytest
    - Coverage > 80%
    - Linting (black, flake8, mypy)

  frontend-tests:
    - Run vitest
    - Coverage > 70%
    - Linting (eslint, prettier)
    - Mobile viewport tests

  build:
    - Build Docker images
    - Push to registry

  deploy:
    - Deploy to staging
    - Run smoke tests
    - Deploy to production
```

---

## 📱 Mobile-Specific Considerations

### 1. Touch Gestures
```typescript
// Swipe to delete document
<Swipeable
  onSwipeLeft={() => confirmDelete(doc.id)}
  threshold={100}
>
  <DocumentCard doc={doc} />
</Swipeable>
```

### 2. Offline Support
```typescript
// Service Worker for offline caching
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}

// Cache API responses
cache.put(request, response.clone())
```

### 3. Network Optimization
```typescript
// Detect connection type
if (navigator.connection?.effectiveType === '4g') {
  // Load high-quality images
} else {
  // Load optimized images
}
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-20
