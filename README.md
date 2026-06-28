# Simple Uptime Monitoring Service

Simple Uptime Monitoring Service is a FastAPI-based web application that lets users register, add URLs to monitor, and view uptime, response latency, check history, and email alerts when a monitored target goes down or recovers. The app uses PostgreSQL for persistent data, Redis for latest status caching, an async background monitor for periodic URL checks, and a single-page frontend served by FastAPI.

## Links

- Video demo: `https://www.awesomescreenshot.com/video/54043778?key=0b7c92b76efc32a819c05ccbc3c2bb48`
- Live HTTPS deployment: `https://up-monitor.live`

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy asyncio
- PostgreSQL 14
- Redis 6 Alpine
- aiohttp
- python-jose JWT authentication
- passlib bcrypt password hashing
- aiosmtplib email alerting
- Docker and Docker Compose
- Nginx reverse proxy
- Certbot SSL certificates
- Vanilla HTML, CSS, JavaScript, and Chart.js

## Features

- User registration and login with JWT bearer tokens
- Password hashing with bcrypt
- Authenticated target management
- URL validation for `http://` and `https://`
- Background monitor loop that checks all active targets every 60 seconds
- Concurrent target checks using `asyncio.gather`
- Persistent time-series check records in PostgreSQL
- Latest status cache in Redis
- 24-hour and 7-day uptime statistics
- Latency history chart
- Soft delete for targets so historical checks are preserved
- Email alerts for down and recovery transitions
- Static single-page dashboard mounted from FastAPI
## Architecture
![alt text](architecture.svg)
 
## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/TesfamichaelA-code/uptime-monitor.git
cd uptime-monitor
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Open `.env` and fill in real values:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@postgres:5432/uptime
REDIS_URL=redis://redis:6379
SECRET_KEY=replace-with-a-generated-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-gmail-address@gmail.com
SMTP_PASS=your-gmail-app-password
```

Generate a strong `SECRET_KEY` with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Important: never commit `.env`. It contains secrets. Only `.env.example` should be committed.

### 3. Start the application

Use Docker Compose v2:

```bash
docker compose up -d --build
```

Docker Compose v1 (`docker-compose`) is no longer maintained and can fail on newer Docker Engine versions with `KeyError: 'ContainerConfig'`.

### 4. Verify the containers

```bash
docker compose ps
```

All three services should show as running:

- `postgres`
- `redis`
- `fastapi-app`

### 5. Open the app

Open:

```text
http://localhost:8000
```

The login/register screen should load. After registering, add monitored URLs and wait about 60 seconds for the first monitor cycle to populate status data.

## API Endpoints

### Health

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/health` | No | Returns `{"status": "ok"}` |

### Authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | No | Register a user and return a JWT access token |
| POST | `/api/auth/login` | No | Log in and return a JWT access token |

Register request:

```json
{
  "email": "student@example.com",
  "password": "password123",
  "notification_email": "student@example.com"
}
```

Login request:

```json
{
  "email": "student@example.com",
  "password": "password123"
}
```

Both endpoints return:

```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

### Targets

All target endpoints require:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/targets` | Yes | Add a monitored target |
| GET | `/api/targets` | Yes | List active targets with latest Redis status |
| DELETE | `/api/targets/{id}` | Yes | Soft delete a target |
| GET | `/api/targets/{id}/stats` | Yes | Return 24-hour and 7-day uptime statistics |
| GET | `/api/targets/{id}/history` | Yes | Return the latest 100 check records |

Create target request:

```json
{
  "name": "Google",
  "url": "https://google.com"
}
```

Newly added targets return `is_up: null` until the background monitor checks them. The frontend displays this state as pending.

## Monitoring Behavior

The monitor starts when the FastAPI application starts. Every 60 seconds it:

1. Queries all active targets from PostgreSQL.
2. Sends concurrent `HEAD` requests with a 10-second timeout.
3. Inserts one `Check` row for every attempt, including failures.
4. Stores the newest status in Redis under `status:{target_id}`.
5. Sends an initial status email on the first check, then sends email alerts only when the status changes.

After the first check, users receive another email only when a target changes from up to down or from down back to up.

## Deployment

The production setup uses:

- Azure B2s Ubuntu VM
- Docker Compose
- Nginx reverse proxy
- Custom domain
- Certbot HTTPS certificate
