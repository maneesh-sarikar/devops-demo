TaskFlow – Containerized Task Management Application
A full-stack task management application demonstrating containerization, multi-service orchestration, REST API development, database integration, reverse proxy configuration, and persistent storage using Podman.
Tech Stack
LayerTechnologyFrontendReact 19, ViteWeb Server / Reverse ProxyNginxBackendPython 3.12, FastAPI, UvicornDatabasePostgreSQL 17Database DriverPsycopgContainerizationPodmanOrchestrationPodman ComposeAPI TestingBruno
Architecture
The application runs as three independent containers:
Frontend: React production build served by Nginx. Nginx serves the UI and forwards /api/ requests to the backend.
Backend: FastAPI handles REST API requests, application logic, and database operations.
Database: PostgreSQL stores task records using persistent named-volume storage.
All three services communicate through the internal Compose network.
Service Communication
Browser
   |
   | http://localhost:5173
   v
Frontend (Nginx :80)
   |
   | backend:8000
   v
Backend (FastAPI :8000)
   |
   | db:5432
   v
PostgreSQL (:5432)
   |
   v
Persistent Volume (postgres_data)
Only the frontend port is published to the host. Backend and database ports remain internal to the container network.
Features
Create, retrieve, update, and delete tasks
Mark tasks as completed or pending
Search and filter tasks
Dashboard with task statistics
PostgreSQL persistent storage
REST API integration
Structured backend logging
API documentation through Swagger UI
Project Structure
devops-demo/
├── api/
│   └── main.py
├── app/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── bruno/
├── nginx/
│   └── default.conf
├── .dockerignore
├── .env.example
├── .gitignore
├── Containerfile
├── compose.yaml
├── README.md
└── requirements.txt
Prerequisites
Podman Desktop
Podman CLI
Podman Compose provider
Git
Environment Configuration
Create your local environment file from the example:
copy .env.example .env
Configure the database credentials in .env.
The .env file contains local configuration and should not be committed to Git. Use .env.example as the configuration template.
Build and Run
Navigate to the project directory:
cd devops-demo
Validate the Compose configuration:
podman compose config
Build the application images:
podman compose build
Start all services:
podman compose up -d
Check running containers:
podman ps
Application Access
ServiceURLTaskFlow Frontendhttp://localhost:5173API Healthhttp://localhost:5173/api/API Documentationhttp://localhost:5173/api/docsDatabase Healthhttp://localhost:5173/api/db-checkOpenAPI Definitionhttp://localhost:5173/api/openapi.json
API Testing
Bruno is used to test API functionality, including:
MethodEndpointOperationGET/tasksRetrieve tasksPOST/tasksCreate a taskPUT/tasks/{task_id}Update a taskDELETE/tasks/{task_id}Delete a taskGET/db-checkVerify database connectivity
Swagger UI is also available for interactive API testing.
Database Inspection
Connect to PostgreSQL using:
podman exec -it devops-postgres psql -U devuser -d devdb
Useful PostgreSQL commands:
\dt
SELECT * FROM tasks;
\d tasks
\q
Data Persistence
PostgreSQL uses a named volume (postgres_data) to preserve database records independently of the database container.
Stop and remove the application containers:
podman compose down
Restart the services:
podman compose up -d
The database volume is preserved when using podman compose down.
Note: Avoid podman compose down -v unless you intentionally want to remove the named volume and its stored data.
Useful Commands
CommandPurposepodman psView running containerspodman ps -aView all containerspodman imagesList container imagespodman compose configValidate Compose configurationpodman compose buildBuild application imagespodman compose up -dStart servicespodman compose logsView service logspodman compose downStop and remove servicespodman volume lsList volumespodman network lsList networks
Troubleshooting
View backend logs:
podman logs devops-backend --tail 50
View frontend logs:
podman logs devops-frontend --tail 30
View database logs:
podman logs devops-postgres --tail 30
If Nginx retains an outdated backend container address after a backend replacement, restart the frontend container:
podman restart devops-frontend
Project Objective
Demonstrate a containerized full-stack application with independent frontend, backend, and database services, internal service communication, reverse proxy configuration, persistent storage, REST API development, and API testing using Podman and Podman Compose.
 
 