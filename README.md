# Organization Management Service

A FastAPI-based multi-tenant Organization Management Service using MongoDB, Docker, and JWT authentication. It supports creating and managing organizations in a multi-tenant style with per-organization collections and admin users.

---

## Features

- Create organizations with:
  - Unique organization name
  - Dynamic MongoDB collection: org_<sanitized_org_name>
  - Admin user for each organization
- Master database storing:
  - Organization metadata (name, collection name, admin email)
  - Admin user credentials (securely hashed)
- Admin login with JWT (Bearer token):
  - Token includes admin email (sub), organization name, and organization id
- Update organization:
  - Rename organization
  - Migrate data to a new collection
  - Update admin email and password
- Delete organization:
  - Only by authenticated admin of that organization
  - Drops org collection and cleans up metadata
- Dockerized setup with docker-compose for API + MongoDB

---

## Tech Stack

- Language: Python 3.11
- Framework: FastAPI
- Database: MongoDB (via async driver Motor)
- Auth: JWT (JSON Web Token)
- Password Hashing: passlib with pbkdf2_sha256
- Config: Environment variables via .env
- Containerization: Docker & Docker Compose

---

## Architecture Overview

### Master Database

A single MongoDB database (configured by MASTER_DB_NAME in .env) holds global metadata:

- organizations collection:
  - organization_name
  - collection_name (e.g., org_testcorp)
  - admin_email
  - created_at, updated_at
- admins collection:
  - email
  - hashed_password
  - organization_name
  - organization_id
  - is_active
  - created_at

### Dynamic Collections

For each organization:

- A new collection is created with the pattern:  
  org_<organization_name> (sanitized to lowercase and non-alphanumerics replaced with _).
- On creation, the collection is initialized with a small metadata document (optional but present).

### High-Level Flow

Client (Swagger / Postman / Frontend)
|
v
FastAPI (app.main:app)

/org/create, /org/get, /org/update, /org/delete

/admin/login (JWT)
|
v
Service Layer

OrganizationService

AuthService
|
v
MongoDB (single DB)

organizations

admins

org_<tenant1>

org_<tenant2>

...

text

---

## Project Structure

.
├── app
│ ├── init.py
│ ├── main.py # FastAPI app, routers, lifespan
│ ├── config.py # Settings via environment variables
│ ├── database.py # Motor client, DB access helpers
│ ├── models
│ │ ├── init.py
│ │ ├── organization.py # Internal Pydantic models
│ │ └── admin.py
│ ├── schemas
│ │ ├── init.py
│ │ ├── organization.py # Request/response models (DTOs)
│ │ └── admin.py
│ ├── services
│ │ ├── init.py
│ │ ├── organization_service.py # Org CRUD & multi-tenant logic
│ │ └── auth_service.py # Admin auth & JWT
│ ├── api
│ │ ├── init.py
│ │ ├── organization.py # /org/* endpoints
│ │ ├── admin.py # /admin/login endpoint
│ │ └── dependencies.py # Auth dependencies (current_admin)
│ └── utils
│ ├── init.py
│ ├── password_handler.py # Password hashing & verification
│ └── jwt_handler.py # JWT encode/decode helpers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md

text

---

## Setup (Without Docker)

### 1. Prerequisites

- Python 3.11+
- MongoDB running locally (default mongodb://localhost:27017)

### 2. Clone and enter project

git clone <your-repo-url>.git
cd organization-management-service

text

### 3. Create and activate virtual environment

Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

Linux / macOS
python -m venv venv
source venv/bin/activate

text

### 4. Install dependencies

pip install -r requirements.txt

text

### 5. Configure environment variables

Create .env in the project root:

MONGODB_URL=mongodb://localhost:27017
MASTER_DB_NAME=master_database
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

text

### 6. Run FastAPI app

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

text

Shubham(SRM), [22:33]
Open Swagger UI:

http://localhost:8000/docs

text

---

## Setup with Docker

### 1. Requirements

- Docker Desktop (or Docker Engine)
- Docker Compose plugin

### 2. Environment

Ensure .env exists in the project root. For Docker, Mongo hostname is the service name:

MONGODB_URL=mongodb://mongo:27017
MASTER_DB_NAME=master_database
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

text

### 3. Build and run

docker compose build
docker compose up

text

The API will be available at:

http://localhost:9000/docs

text

To stop:

docker compose down

text

---

## API Endpoints

### 1. Create Organization

POST /org/create

Body:

{
"organization_name": "TestCorp",
"email": "admin@testcorp.com",
"password": "Abc123!"
}

text

Behavior:

- Validates that organization_name is unique.
- Creates a collection org_testcorp.
- Inserts organization metadata into organizations.
- Creates an admin entry in admins with hashed password.
- Returns basic org metadata.

---

### 2. Get Organization by Name

GET /org/get?organization_name=TestCorp

Response (example):

{
"organization_name": "TestCorp",
"collection_name": "org_testcorp",
"admin_email": "admin@testcorp.com",
"created_at": "2025-12-12T15:39:43.749036",
"updated_at": "2025-12-12T15:39:43.749036"
}

text

Returns 404 if organization does not exist.

---

### 3. Admin Login

POST /admin/login

Body:

{
"email": "admin@testcorp.com",
"password": "Abc123!"
}

text

Response:

{
"access_token": "<jwt-token>",
"token_type": "bearer",
"admin_email": "admin@testcorp.com",
"organization_name": "TestCorp"
}

text

JWT payload includes:

- sub: admin email
- organization_name
- organization_id

Use this token as:

Authorization: Bearer <access_token>

text

on protected endpoints.

---

### 4. Update Organization (Protected)

PUT /org/update?old_organization_name=TestCorp

Requires JWT in Authorize.

Body:

{
"organization_name": "TestCorp2",
"email": "newadmin@testcorp.com",
"password": "NewPass123"
}

text

Behavior:

- Verifies the authenticated admin belongs to old_organization_name.
- Ensures new organization_name is not already used.
- Creates new collection (e.g., org_testcorp2).
- Copies documents from old collection.
- Updates organizations and admins metadata.
- Drops old collection if name changed.

---

### 5. Delete Organization (Protected)

DELETE /org/delete?organization_name=TestCorp2

Requires JWT in Authorize.

Behavior:

- Verifies admin belongs to the organization.
- Drops the organization’s collection.
- Deletes all admin entries for that org.
- Deletes the organization record from organizations.

---

## Design Choices & Trade-offs

- Single DB, multiple collections per tenant:  
  Simple and efficient for a moderate number of organizations; all tenants share a DB with logically isolated collections.
- JWT-based, stateless auth:  
  Tokens carry admin and organization info, making the system easy to scale horizontally since no session store is required.
- PBKDF2 for password hashing:  
  Secure password storage using key-stretching and avoiding bcrypt’s 72‑byte password length limit.

Possible improvements:

- Separate MongoDB databases per tenant for stronger isolation at very large scale.
- Add caching (e.g., Redis) for frequently accessed organization metadata.
- Implement refresh tokens and logout/blacklist if needed.
- Introduce background jobs for heavy collection migrations in PUT /org/update.

---

## Submission Notes

Include in your submission:

- GitHub repository URL containing:
  - Source code (app/ etc.)
  - Dockerfile and docker-compose.yml
  - This README.md
- Optional:
  - Image of the high-level architecture diagram.
  - Short notes further explaining multi-tenant design decisions.
