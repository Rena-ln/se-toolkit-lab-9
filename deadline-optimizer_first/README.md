# Assignment Deadline Optimizer

AI-powered personal deadline tracker that analyzes your workload, prioritizes tasks by urgency and complexity, and tells you exactly what to work on and when.

**Author:** Irina Kostina (i.kostina@innopolis.university) — Group CSE-04

## Demo

![Task List View](docs/screenshots/task-list.png)
*Prioritized task list with AI recommendations*

![Dashboard View](docs/screenshots/dashboard.png)
*Analytics dashboard with progress tracking*

### Product Context

**End Users:** University students managing multiple courses, assignments, and exams each semester.

**Problem:** Students face 4–5 overlapping deadlines every week, don't know where to start, panic, and end up submitting late or producing low-quality work.

**Solution:** The Assignment Deadline Optimizer doesn't just display deadlines — it builds a personalized action plan based on urgency, assignment weight, estimated effort, and past performance, so students always know exactly what to work on next.

## Features

### Implemented ✅
- **Unified calendar of deadlines** across all courses
- **AI-powered task prioritization** — computes priority scores based on urgency, weight, status, and priority level
- **Personalized agent recommendations** — "Start with Physics lab — it's the heaviest and worth 20%"
- **Conflict warnings** for overlapping deadlines
- **Per-course progress tracking** with completion percentages
- **Completed task history and productivity stats**
- **Create/Delete assignments and deadlines** through the web UI
- **React dashboard** with task list, charts, and management panel
- **FastAPI backend** with full CRUD REST API
- **PostgreSQL database** with sample data
- **MCP server** with 7 tools for AI agent integration
- **Docker Compose** — all services containerized
- **Reverse proxy** via Caddy
- **Observability** — OpenTelemetry + VictoriaLogs + VictoriaTraces

### Not Yet Implemented 🔲
- Calendar view (grid layout)
- User authentication (single shared API key currently)
- Nanobot agent live deployment (requires LLM provider)
- Telegram bot (blocked on university VMs)
- Mobile app

## Usage

1. Open `http://<vm-ip>:8080` in a browser
2. Enter the API key: `dev-api-key-change-in-production`
3. View prioritized tasks with AI recommendations on the **📋 Tasks** tab
4. Check progress charts on the **📊 Dashboard** tab
5. Create/delete assignments and deadlines on the **⚙️ Manage** tab
6. Access API docs at `http://<vm-ip>:8080/docs`

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/courses/` | List all courses |
| POST | `/api/v1/courses/` | Create a course |
| GET | `/api/v1/assignments/` | List assignments |
| POST | `/api/v1/assignments/` | Create an assignment |
| DELETE | `/api/v1/assignments/{id}` | Delete an assignment |
| POST | `/api/v1/deadlines/` | Create a deadline |
| DELETE | `/api/v1/deadlines/{id}` | Delete a deadline |
| POST | `/api/v1/analytics/prioritize` | **Core feature** — get prioritized tasks |
| GET | `/api/v1/analytics/progress` | Per-course progress |
| GET | `/api/v1/analytics/conflicts` | Deadline conflict detection |
| GET | `/api/v1/analytics/productivity` | Productivity statistics |

## Deployment

### Prerequisites

- **OS:** Ubuntu 24.04 (or any Linux with Docker)
- **Installed:** Docker, Docker Compose, Node.js 18+ (for frontend build)

### Step-by-step

```bash
# 1. Clone the repository
git clone <repo-url>
cd deadline-optimizer

# 2. Configure environment
cp .env.docker.example .env.docker.secret
# Edit .env.docker.secret — set your API keys if needed

# 3. Start all services
docker compose up -d

# 4. Wait for PostgreSQL to be healthy (about 10 seconds)
docker compose ps

# 5. Build frontend (on the VM)
cd client-web-react
npm install
npx vite build
docker cp dist/. do-caddy:/srv/
cd ..

# 6. Open in browser
# http://localhost:8080
```

### Services

| Service | Port | Description |
|---|---|---|
| Caddy (proxy) | 8080 | Reverse proxy + SPA serving |
| Backend (FastAPI) | internal:8000 | REST API |
| PostgreSQL | 54321 | Database |
| PgAdmin | 54320 | Database admin UI |
| VictoriaLogs | 42010 | Log storage |
| VictoriaTraces | 42011 | Trace storage |
| OpenTelemetry | 4317, 4318 | OTLP receiver |

### Architecture

```
[Browser] -- React SPA --> Caddy --> Backend (FastAPI) --> PostgreSQL
                                                     |
[Nanobot Agent] <-- MCP tools --> Deadline MCP Server
                      |
                      +--> LLM Provider (Qwen Code API)
                      +--> Observability: VictoriaLogs / VictoriaTraces
```
