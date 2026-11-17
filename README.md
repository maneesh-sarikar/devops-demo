
cat > README.md <<'EOF'
# DevOps Demo Application

A containerized REST API application built using FastAPI and PostgreSQL, deployed locally using Podman and Podman Compose.

## Technology Stack

| Component | Technology |
|---|---|
| API | Python, FastAPI |
| Database | PostgreSQL 17 |
| Container Runtime | Podman |
| Container Orchestration | Podman Compose |
| API Testing | Bruno |
| API Documentation | Swagger UI |

## Project Structure

```text
devops-demo/
├── app/
│   └── main.py
├── bruno/
│   └── DevOps Demo API/
├── .env.example
├── .gitignore
├── Containerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

## Prerequisites

- Podman Desktop
- Podman CLI
- Podman Compose
- Git

## Setup and Execution

1. Clone the repository.

2. Create your environment file:

   ```bash
   cp .env.example .env
   ```

3. Update the values in `.env` as required.

4. Build and start the application:

   ```bash
   podman-compose up -d --build
   ```

5. Check running containers:

   ```bash
   podman ps
   ```

## Application URLs

| Resource | URL |
|---|---|
| API Health Check | http://localhost:8000/ |
| Database Check | http://localhost:8000/db-check |
| Swagger Documentation | http://localhost:8000/docs |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API health check |
| GET | /db-check | Database connectivity |
| POST | /tasks | Create a task |
| GET | /tasks | Retrieve all tasks |
| PUT | /tasks/{task_id} | Update a task |
| DELETE | /tasks/{task_id} | Delete a task |

## API Testing

The Bruno collection is available in:

`bruno/DevOps Demo API/`

Import or open this collection in Bruno to execute the API requests.

## Database Persistence

PostgreSQL data is stored in a named Podman volume, allowing data to persist when containers are stopped and recreated.

## Stop the Application

```bash
podman-compose down
```

To remove the application and its database volume:

```bash
podman-compose down -v
```

**Warning:** The second command permanently removes the database volume and its stored data.

EOF
