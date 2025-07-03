# fastapi-base

## ✅ Features Implemented

### 🧠 Core Design
- Modular folder structure (`app/`, `settings/`, `user/`, etc.)
- Separation of concerns: routes, schemas, config, caching, logging

### Foldr Structure
```bash
fastapi-base
├── .env
├── .env.example
├── .gitignore
├── app
│   ├── __init__.py
│   ├── admin_test
│   │   ├── __init__.py
│   │   └── route.py
│   ├── app.py
│   ├── default
│   │   ├── __init__.py
│   │   └── route.py
│   ├── middlewares
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── migrations
│   │   ├── __init__.py
│   │   └── associations.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── caching.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── logging.py
│   │   ├── monitor.py
│   │   └── ratelimiter.py
│   ├── static
│   │   ├── __init__.py
│   │   └── status.html
│   ├── user
│   │   ├── __init__.py
│   │   ├── route.py
│   │   └── schema.py
│   └── utils
│       ├── __init__.py
│       ├── cb_utils.py
│       ├── circuit_breaker.py
│       └── redis_cache.py
├── LICENSE
├── README.md
├── Dockerfile
└── requirements.txt
```

### 🧾 API Functionality
- `POST /api/user` → Create user (MongoDB-backed, handles duplicates)
- `GET /api/user/{id}` → Fetch user by `id` (with async caching)
- `GET /api/user/test` → Test endpoint using background tasks (non-blocking)

### 🔐 Authentication & Authorization
- JWT-based auth using `python-jose`
- RS256 token validation via public key
- Role-based access control (`extension_Roles`)
- Public endpoints bypass auth (`ENVIRONMENT` controlled)
- Middleware applies auth logic globally

### 🧱 Middleware & Infrastructure
- Background tasks support (via FastAPI's `BackgroundTasks`)
- Redis caching via `cachetools_async` + `redis_cache.py`
- Rotating file logging + colored console logs (`logging.py`)
- `.env` config support via `config.py`
- Rate limiting + monitoring scaffolding in place

---

## 🛠 Run Server

### ▶️ Development (with hot reload)

```bash
uvicorn app:app --reload
```

### 🔐 Production (Uvicorn, multiple workers)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### 🛡 Production (Gunicorn + Uvicorn workers)

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
```

---

## ⏭️ Suggested Next Steps

- [ ] Circuit breaker for external calls (e.g., `pybreaker`)
- [ ] Unit tests (e.g., `pytest`, `httpx`)
- [ ] API versioning (e.g., `/v1/api/`)
- [ ] Dockerfile for containerization
- [ ] OpenAPI security scheme definitions

---
