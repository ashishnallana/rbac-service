# Secure Authentication & Authorization Service

A centralized, stateless authentication service built with FastAPI, PostgreSQL, and Redis. It provides secure identity verification (JWT), handles long-lived refresh tokens, enforces Role-Based Access Control (RBAC), and protects against brute-force attacks using Redis-based rate limiting.

## Features

- **Stateless Authentication:** JWT-based access tokens (15-minute expiry).
- **Secure Token Rotation:** Refresh tokens stored securely in a Postgres DB (7-day expiry).
- **Role-Based Access Control (RBAC):** Middleware/Dependencies to safeguard specific routes (e.g., `/admin/data`).
- **Rate Limiting:** Protects the `/login` route by tracking attempts per IP + Email using Redis (locks out after 5 rapid failures).
- **Audit Logging:** Every login attempt, token refresh, and logout is audited into the database.
- **Modern Security:** `bcrypt` used for passwords.

## Architecture

```
Client  -->  Auth Service (FastAPI)  <-->  PostgreSQL DB (Users, Tokens, Audits)
                 |
                 v
       Redis (Rate Limiter Cache)
```

**Scalability Consideration:**
The system uses stateless JWTs for authorization, meaning once an access token is issued, validation happens locally without a DB hit. The service can easily scale horizontally. Redis handles distributed rate limiting, and PostgreSQL manages persistent state.

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL Server Running
- Redis Server Running

### 1. Installation

Clone this project and initialize your virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration

Modify `.env` to match your Postgres and Redis configurations:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/rbac_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=generate_a_complex_random_string
```
Make sure `rbac_db` database actually exists in your Postgres instance. Note: the app will automatically generate the corresponding tables on startup.

### 3. Running the Service

```bash
uvicorn app.main:app --reload
```

FastAPI automatically generates an interactive Swagger UI. Visit:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## API Endpoints & Sample Requests

### 1. Signup (`POST /api/auth/signup`)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "admin@example.com",
  "password": "securepassword123"
}'
```

*Note: Newly created accounts default to the `user` role. You can manually change the role to `admin` directly in the database for testing.*

### 2. Login (`POST /api/auth/login`)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "admin@example.com",
  "password": "securepassword123"
}'
```

### 3. Get Profile (`GET /api/user/profile`)
Requires Access Token in Authorization Header.
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/user/profile' \
  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

### 4. Admin Data (`GET /api/admin/data`)
Requires an Access Token corresponding to a user with the `admin` role.
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/admin/data' \
  -H 'Authorization: Bearer <YOUR_ACCESS_TOKEN>'
```

### 5. Refresh Token (`POST /api/auth/refresh`)
Issues a new Access Token & Refresh Token pair, revoking the old one.
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/auth/refresh' \
  -H 'Content-Type: application/json' \
  -d '{
  "refresh_token": "<YOUR_REFRESH_TOKEN>"
}'
```

---
