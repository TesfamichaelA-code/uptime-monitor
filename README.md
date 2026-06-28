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
<svg viewBox="0 0 680 500" xmlns="http://www.w3.org/2000/svg" width="100%" font-family="system-ui, -apple-system, BlinkMacSystemFont, sans-serif">
  <title>Uptime monitoring service — system architecture</title>
  <desc>Web browser connects via HTTPS through Nginx to FastAPI on Azure. FastAPI's async ping loop monitors external target websites every 60 seconds, stores results in PostgreSQL, caches current status in Redis, and sends email alerts via Gmail SMTP on status changes.</desc>

  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Azure VM container -->
  <rect x="15" y="90" width="445" height="385" rx="16" fill="#FAFAF8" stroke="#B4B2A9" stroke-width="1.5" stroke-dasharray="8 4"/>
  <text font-size="11" fill="#888780" x="30" y="107">Azure B2s VM · Docker Compose</text>

  <!-- Browser (outside VM, top left) -->
  <rect x="40" y="20" width="200" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
  <text font-size="14" font-weight="500" fill="#3C3489" x="140" y="43" text-anchor="middle" dominant-baseline="central">Web browser</text>
  <text font-size="12" fill="#534AB7" x="140" y="62" text-anchor="middle" dominant-baseline="central">Dashboard + API calls</text>

  <!-- External target URLs (outside VM, top right) -->
  <rect x="460" y="20" width="205" height="56" rx="8" fill="#F9F8F6" stroke="#B4B2A9" stroke-width="1.5" stroke-dasharray="5 3"/>
  <text font-size="14" font-weight="500" fill="#444441" x="562" y="43" text-anchor="middle" dominant-baseline="central">Target sites</text>
  <text font-size="12" fill="#888780" x="562" y="62" text-anchor="middle" dominant-baseline="central">External · internet</text>

  <!-- Nginx -->
  <rect x="120" y="112" width="220" height="56" rx="8" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
  <text font-size="14" font-weight="500" fill="#444441" x="230" y="136" text-anchor="middle" dominant-baseline="central">Nginx proxy</text>
  <text font-size="12" fill="#5F5E5A" x="230" y="154" text-anchor="middle" dominant-baseline="central">Reverse proxy · TLS 1.3</text>

  <!-- FastAPI outer box -->
  <rect x="40" y="248" width="400" height="82" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
  <text font-size="11" fill="#0F6E56" x="240" y="260" text-anchor="middle" dominant-baseline="central">FastAPI application</text>

  <!-- FastAPI REST inner -->
  <rect x="52" y="266" width="155" height="52" rx="4" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
  <text font-size="13" font-weight="500" fill="#04342C" x="130" y="287" text-anchor="middle" dominant-baseline="central">REST API</text>
  <text font-size="11" fill="#085041" x="130" y="304" text-anchor="middle" dominant-baseline="central">Auth · routing · CRUD</text>

  <!-- FastAPI Async inner -->
  <rect x="224" y="266" width="204" height="52" rx="4" fill="#9FE1CB" stroke="#0F6E56" stroke-width="0.5"/>
  <text font-size="13" font-weight="500" fill="#04342C" x="326" y="287" text-anchor="middle" dominant-baseline="central">Async ping loop</text>
  <text font-size="11" fill="#085041" x="326" y="304" text-anchor="middle" dominant-baseline="central">asyncio · HEAD checks</text>

  <!-- Redis -->
  <rect x="40" y="402" width="150" height="56" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
  <text font-size="14" font-weight="500" fill="#0C447C" x="115" y="426" text-anchor="middle" dominant-baseline="central">Redis</text>
  <text font-size="12" fill="#185FA5" x="115" y="444" text-anchor="middle" dominant-baseline="central">Status cache</text>

  <!-- PostgreSQL -->
  <rect x="222" y="402" width="180" height="56" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
  <text font-size="14" font-weight="500" fill="#0C447C" x="312" y="426" text-anchor="middle" dominant-baseline="central">PostgreSQL</text>
  <text font-size="12" fill="#185FA5" x="312" y="444" text-anchor="middle" dominant-baseline="central">Checks · users</text>

  <!-- Gmail SMTP (outside VM) -->
  <rect x="470" y="402" width="170" height="56" rx="8" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
  <text font-size="14" font-weight="500" fill="#633806" x="555" y="426" text-anchor="middle" dominant-baseline="central">Gmail SMTP</text>
  <text font-size="12" fill="#854F0B" x="555" y="444" text-anchor="middle" dominant-baseline="central">Alert emails</text>


  <!-- ARROW 1: Browser → Nginx (L-path) -->
  <path d="M140,76 L140,104 L230,104 L230,112" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arr)"/>
  <text font-size="11" fill="#5F5E5A" x="186" y="100" text-anchor="middle">HTTPS / REST</text>

  <!-- ARROW 2: Nginx → FastAPI REST section (L-path, routes to REST half) -->
  <path d="M230,168 L230,210 L130,210 L130,248" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- ARROW 3: FastAPI Async → External target URLs (dashed, exits VM) -->
  <path d="M440,287 L562,287 L562,76" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#arr)"/>
  <text font-size="11" fill="#5F5E5A" x="576" y="192" text-anchor="start">HEAD polls</text>
  <text font-size="11" fill="#5F5E5A" x="576" y="207" text-anchor="start">every 60s</text>

  <!-- ARROW 4: FastAPI → Redis -->
  <path d="M115,330 L115,402" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arr)"/>
  <text font-size="10" fill="#5F5E5A" x="108" y="367" text-anchor="end">sub-1ms</text>

  <!-- ARROW 5: FastAPI → PostgreSQL -->
  <path d="M312,330 L312,402" fill="none" stroke="#888780" stroke-width="1.5" marker-end="url(#arr)"/>
  <text font-size="10" fill="#5F5E5A" x="320" y="367" text-anchor="start">check log</text>

  <!-- ARROW 6: FastAPI → Gmail SMTP (dashed amber, exits VM on status change) -->
  <path d="M440,322 L555,322 L555,402" fill="none" stroke="#854F0B" stroke-width="1.5" stroke-dasharray="5 3" marker-end="url(#arr)"/>
  <text font-size="10" fill="#854F0B" x="448" y="317" text-anchor="start">on status change</text>

</svg>

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
