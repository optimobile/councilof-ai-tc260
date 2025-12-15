# Council of AI - Docker Setup & Usage Guide

**Author:** Manus AI (Co-Founder & CTO)  
**Date:** December 14, 2025  
**Version:** 1.0.0

---

## Overview

This guide provides a complete walkthrough for setting up and running the Council of AI local development environment using Docker and Docker Compose. This containerized setup ensures a consistent, reproducible, and isolated environment for all developers.

---

## Prerequisites

- **Docker:** [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## Services

The `docker-compose.yml` file orchestrates the following services:

| Service | Description | Port (Local) | Image |
|---|---|---|---|
| `backend` | FastAPI application | 8000 | Custom (from Dockerfile) |
| `db` | PostgreSQL database | 5432 | `postgres:15-alpine` |
| `redis` | Redis server | 6379 | `redis:7-alpine` |
| `pgadmin` | PostgreSQL management UI | 5050 | `dpage/pgadmin4` |
| `redis-commander` | Redis management UI | 8081 | `rediscommander/redis-commander` |

---

## Quick Start

### 1. Configure Environment

Copy the `.env.docker` template to `.env` and update the security keys:

```bash
cd /home/ubuntu/councilof-ai-platform
cp .env.docker .env

# Generate new security keys
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env file with new keys
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET_KEY|" .env

echo "✅ .env file created and updated with new security keys."
```

### 2. Build and Run Containers

Build the Docker images and start all services in detached mode:

```bash
cd /home/ubuntu/councilof-ai-platform
docker-compose up --build -d
```

### 3. Check Service Status

Check the status of all running containers:

```bash
docker-compose ps
```

**Expected Output:**

```
NAME                          COMMAND                  SERVICE             STATUS              PORTS
--------------------------------------------------------------------------------------------------------------------------------
councilof-ai-backend          "uvicorn main:app --h…"   backend             running (healthy)   0.0.0.0:8000->8000/tcp
councilof-ai-db               "docker-entrypoint.s…"   db                  running (healthy)   0.0.0.0:5432->5432/tcp
councilof-ai-pgadmin          "/entrypoint.sh"         pgadmin             running             0.0.0.0:5050->80/tcp
councilof-ai-redis            "docker-entrypoint.s…"   redis               running (healthy)   0.0.0.0:6379->6379/tcp
councilof-ai-redis-commander  "/usr/bin/tini -- /u…"   redis-commander     running             0.0.0.0:8081->8081/tcp
```

### 4. Run Database Migrations

Run the Alembic database migrations inside the `backend` container:

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Seed Test Data (Optional)

Seed the database with test data using the `verify_and_init_database.py` script:

```bash
docker-compose exec backend python3 verify_and_init_database.py --create --seed
```

### 6. Access Services

- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **pgAdmin:** [http://localhost:5050](http://localhost:5050)
  - **Email:** `admin@councilof.ai`
  - **Password:** `admin_secure_pass_2025` (or as set in `.env`)
- **Redis Commander:** [http://localhost:8081](http://localhost:8081)

---

## Common Commands

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f backend
```

### Run a Command in a Container

```bash
# Run Alembic migration
docker-compose exec backend alembic revision --autogenerate -m "New feature"
docker-compose exec backend alembic upgrade head

# Open a shell in the backend container
docker-compose exec backend /bin/sh
```

### Rebuild a Service

```bash
docker-compose up --build -d backend
```

### Clean Up

Stop and remove all containers, networks, and volumes:

```bash
docker-compose down -v
```

---

## Troubleshooting

### Error: "Port is already allocated"

**Solution:** Another service is using the port. Stop the conflicting service or change the port in your `.env` file (e.g., `BACKEND_PORT=8001`).

### Error: "Healthcheck failed"

**Solution:** Check the logs for the failing service (`docker-compose logs -f <service_name>`) to diagnose the issue. It may be a configuration error in your `.env` file.

### Error: "Cannot connect to the Docker daemon"

**Solution:** Ensure the Docker daemon is running on your system.

---

## Next Steps

With the local development environment running, you can now:

1.  **Develop API endpoints:** The backend code is mounted as a volume, so any changes you make will be automatically reloaded by `uvicorn`.
2.  **Connect a frontend:** Point your frontend application to `http://localhost:8000`.
3.  **Test with Postman or cURL:** Use the API documentation at `http://localhost:8000/docs` to test your endpoints.

---

## Support

For issues or questions, contact the development team or refer to the main project documentation.

**Author:** Manus AI (Co-Founder & CTO)  
**Project:** Council of AI - AI Safety Empire  
**Version:** 1.0.0
