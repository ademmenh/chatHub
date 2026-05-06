# ChatHub API

A FastAPI Messaging backend with Domain-Driven Design (DDD) architecture.

## Features

- **Architecture**: Domain-Driven Design (DDD) with clear separation of concerns.
- **Messaging**: RabbitMQ with Outbox Pattern for reliable event delivery.
- **WebSockets**: Socket.IO integration for real-time notifications.
- **Database**: PostgreSQL with SQLAlchemy 2.0 (Async) and Alembic migrations.
- **Auth**: JWT-based authentication with Refresh Tokens.

## Tech Stack

- **Language**: Python 3.12
- **Framework**: FastAPI + python-socketio
- **Database**: PostgreSQL (SQLAlchemy + asyncpg)
- **Broker**: RabbitMQ (aio-pika)
- **Validation**: Pydantic v2
- **Reverse Proxy**: NGINX

## Project Structure

```
src/
	main.py              # App entry point, router registration
	config.py            # Settings from environment variables
	database.py          # SQLAlchemy async engine, Base, get_db
	shared/
		errors/          # AppError, exception handlers
		middleware/      # JWT auth dependency, role guards
	auth/                # Login use case, JWT adapter, password adapter
		domain/
		application/
		infrastructure/
		presentation/
		tests/
	users/               # User CRUD — domain
```

## DDD Layer Convention

- `domain/` — Pure business logic: entities, value objects, and port interfaces.
- `application/` — Orchestration: use cases that implement user stories.
- `infrastructure/` — Technical details: DB repositories, external API adapters, messaging.
- `presentation/` — Entry points: REST controllers, DTOs, Socket.IO event handlers.

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) installed locally.
- Docker and Docker Compose.

### Development

1. **Setup Environment**:
   ```bash
   cp .env.example .env.dev
   ```

2. **Run with Docker Compose**:
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

3. **Run**:
   ```bash
   make build:dev
   make start:dev
   ```

### Production Environment

```bash
make build:prod
make start:prod
```

## License

This project is licensed under the GPL v3 License.
