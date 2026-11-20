# Intelligent ERP Agent Engine 🤖📦

A production-ready, asynchronous enterprise agent engine built with **FastAPI**, **LangGraph**, **PostgreSQL (pgvector)**, **Redis**, and **Celery**. This system integrates autonomous LLM reasoning loops with deterministic ERP tools, caching, security, rate limiting, and background task offloading.

🚀 **Live Cloud Production Deployment:** [https://intelligent-erp-agent-engine-production.up.railway.app/docs](https://intelligent-erp-agent-engine-production.up.railway.app/docs)

---

## 🏗 System Architecture

```text
                        ┌─────────────────────────────────────────┐
                        │              Client / Frontend          │
                        └────────────────────┬────────────────────┘
                                             │  HTTP / REST (SSL)
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │     Cloud API Gateway / Railway         │
                        │   (OAuth2 / JWT Auth + SlowAPI Limits)  │
                        └──────┬─────────────────┬──────────────┬─┘
                               │                 │              │
                   Agent State │     Tool Output │  Async Jobs  │
                  & Embeddings │        Caching  │   Dispatched │
                               ▼                 ▼              ▼
     ┌────────────────────────────┐ ┌───────────────┐ ┌───────────────────┐
     │   PostgreSQL + pgvector    │ │  Redis Cache  │ │   Redis Broker    │
     │  (Database / State DB)     │ │ (SHA-256 TTL) │ │  (Celery Queue)   │
     └────────────────────────────┘ └───────────────┘ └─────────┬─────────┘
                                                                │
                                                                ▼
                                                      ┌───────────────────┐
                                                      │   Celery Worker   │
                                                      │  (Background PDF) │
                                                      └───────────────────┘
```

---

## ✨ Key Features

- **Cloud Deployed:** Fully containerized multi-service architecture running live on Railway with dynamic private microservice networking.
- **Autonomous Tool Execution:** LangGraph agent orchestrating stock availability checks (`check_inventory_stock`) and dynamic quote pricing calculations (`calculate_order_quote`).
- **In-Memory Tool Caching:** Redis cache layer using SHA-256 hashed argument inputs to serve duplicate tool lookups instantly with configurable TTLs.
- **Enterprise Security:** OAuth2 Bearer token (JWT) authentication safeguarding agent execution routes (`/run` and `/stream`).
- **IP Rate Limiting:** Protected authentication endpoints using `slowapi` to prevent password brute-forcing.
- **Async Task Offloading:** Dedicated Celery background workers for offloading heavy, non-blocking tasks (e.g., PDF quote exports).
- **Containerized Stack:** Docker Compose setup with health checks and persistent volume management across all components.
- **E2E Integration Testing:** Pytest and `pytest-asyncio` integration suite for validating health, auth, state retention, and background workers.

---

## 🚀 Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (Async), AsyncPG, Pydantic v2
- **Agent Orchestration:** LangGraph, LangChain OpenAI
- **Databases & Caching:** PostgreSQL (pgvector v0.8.7), Redis (aioredis)
- **Task Queue:** Celery with Redis Broker & Result Backend
- **Infrastructure:** Railway Cloud Hosting, Docker, Multi-stage Containers
- **Security:** OAuth2, JWT (python-jose), Bcrypt, SlowAPI
- **Testing & Dev:** Pytest, pytest-asyncio, HTTPX, Docker Compose

---

## 📁 Repository Structure

```text
intelligent-erp-agent-engine/
├── app/
│   ├── api/                # FastAPI dependency injection & security wrappers
│   ├── core/               # Security, Celery config, rate limiter setup
│   ├── database/           # SQLAlchemy DB setup & async engine context
│   ├── models/             # Database ORM models
│   ├── routers/            # API endpoint routes (agent, auth, tasks)
│   ├── services/           # Redis caching & external service integrations
│   ├── tools/              # Deterministic ERP agent tools
│   ├── config.py           # Environment settings schema & dynamic URL validators
│   └── main.py             # FastAPI entrypoint & application lifespan
├── tests/                  # Integration and E2E test suite
│   ├── conftest.py         # Pytest fixtures & HTTP async client
│   ├── test_api_e2e.py     # End-to-end API & security tests
│   └── test_rate_limit.py  # SlowAPI rate limit tests
├── docker-compose.yml      # Orchestration stack specification
├── Dockerfile              # Python 3.11 container environment
├── pytest.ini              # Pytest configuration & loop scoping
└── requirements.txt        # Pinned Python package dependencies
```

---

## 🌐 Live Verification & API Usage

Access the live interactive Swagger UI documentation at:
👉 **`https://intelligent-erp-agent-engine-production.up.railway.app/docs`**

### Live Verification Steps
1. Navigate to the live [Swagger Documentation](https://intelligent-erp-agent-engine-production.up.railway.app/docs).
2. Expand `POST /api/v1/auth/login`, click **Try it out**, enter default credentials (`admin` / `admin123`), and execute to generate a signed JWT access token.
3. Click **Authorize 🔓** at the top right of the page and enter your token.
4. Expand `POST /api/v1/agent/run` and submit an agent execution payload:
   ```json
   {
     "prompt": "Check Stock for 6204-2RS",
     "thread_id": "01"
   }
   ```

---

## 🛠 Local Setup & Installation

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- OpenAI API Key.

### 2. Environment Setup
Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=supersecretkey123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/erp_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Build & Run Containers
Launch the stack locally using Docker Compose:

```powershell
docker compose up --build -d
```

Verify that all containers are healthy:
```powershell
docker compose ps
```

---

## 🧪 Running Automated Tests

Run the complete integration test suite inside the container environment:

```powershell
docker compose exec erp_agent_app pytest
```

---

## 📖 API Documentation & Endpoints

### Key Endpoint Routes

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Authenticate user & issue JWT bearer token (Rate limited: 5/min) | No |
| `POST` | `/api/v1/agent/run` | Execute multi-turn agent reasoning loop | Yes (JWT) |
| `POST` | `/api/v1/agent/stream` | Stream real-time agent output tokens | Yes (JWT) |
| `POST` | `/api/v1/tasks/export-quote` | Dispatch non-blocking Celery quote export task | Yes (JWT) |
| `GET` | `/api/v1/tasks/status/{task_id}` | Poll background Celery task state & output payload | Yes (JWT) |
| `GET` | `/health` | Application health check probe | No |

---

## 🛡 Security & Hardening Features

1. **Authentication:** Endpoint access requires valid JWT Bearer tokens created via `/api/v1/auth/login`.
2. **Brute Force Protection:** Authentication routes enforcement limits clients to 5 login attempts per minute per IP address (`slowapi`).
3. **Task Isolation:** Long-running execution runs inside isolated `celery_worker` containers without blocking the FastAPI ASGI event loop.
4. **Cloud Network Isolation:** Database and Redis services communicate exclusively over dynamic private internal hostnames.