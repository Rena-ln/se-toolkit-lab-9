# Assignment Deadline Optimizer — Task 3 Report (Version 1)

## Summary

Version 1 of the Assignment Deadline Optimizer has been implemented and is ready for TA review. The core feature — AI-powered task prioritization — is fully functional.

---

## What was built (Version 1)

### 1. Backend (FastAPI + PostgreSQL)

- **Courses API** — full CRUD for university courses
- **Assignments API** — full CRUD for assignments with course linkage
- **Deadlines API** — create/list/delete deadlines per assignment
- **Analytics API** — the core feature:
  - `POST /analytics/prioritize` — returns prioritized task list with:
    - Computed priority score (based on urgency, weight, status, priority level)
    - Human-readable recommendation for each task
    - Risk level assessment (low, medium, high, critical)
    - Conflict warnings for overlapping deadlines
  - `GET /analytics/progress` — per-course progress tracking
  - `GET /analytics/conflicts` — deadline conflict detection
  - `GET /analytics/productivity` — completion statistics and performance metrics
- **Health check** endpoint at `/health`

### 2. Database

- PostgreSQL 17 with async SQLAlchemy
- Three tables: `courses`, `assignments`, `deadlines`
- Enums for priority levels and assignment status
- Foreign key relationships with cascade delete
- Sample data: 5 courses, 12 assignments, 12 deadlines

### 3. Frontend (React SPA)

- **Login screen** — API key authentication
- **Task List view** — prioritized tasks with:
  - Color-coded urgency bars
  - Priority score badges
  - Course name with color coding
  - Status, type, weight, estimated time metadata
  - AI-generated recommendation text
  - Conflict warnings (when applicable)
- **Dashboard view** — charts and tables:
  - Course completion rate bar chart
  - Task status distribution doughnut chart
  - Workload by course bar chart
  - Detailed progress table with completion percentages
  - Overall statistics cards

### 4. MCP Server (AI Agent Tools)

Seven tools available to the Nanobot agent:
1. `get_prioritized_tasks` — fetch prioritized recommendations
2. `get_courses` — list all courses
3. `get_assignments` — list assignments
4. `get_progress_overview` — get progress stats
5. `get_deadline_conflicts` — detect conflicts
6. `get_productivity_stats` — get productivity metrics
7. `update_assignment_status` — update task status

### 5. Infrastructure

- Docker Compose with 9 services
- Caddy reverse proxy routing API and SPA
- OpenTelemetry collector for observability
- VictoriaLogs for log storage
- VictoriaTraces for trace storage

---

## Self-testing performed

| Test | Result |
|---|---|
| `GET /health` returns 200 | ✅ Pass |
| `GET /api/v1/courses/` returns 5 courses | ✅ Pass |
| `GET /api/v1/assignments/` returns 12 assignments | ✅ Pass |
| `POST /api/v1/analytics/prioritize` returns scored tasks | ✅ Pass |
| `GET /api/v1/analytics/progress` returns progress data | ✅ Pass |
| `GET /api/v1/analytics/conflicts` returns conflicts | ✅ Pass |
| Frontend loads at `http://localhost:8080` | ✅ Pass |
| Frontend displays task list with recommendations | ✅ Pass |
| Frontend displays dashboard with charts | ✅ Pass |
| All Docker containers running | ✅ Pass |

## Bugs found and fixed during self-testing

1. **Missing `Boolean` import in models** — `NameError` on startup. Fixed by adding `Boolean` to SQLAlchemy imports.
2. **Frontend build missing** — Caddy returned 404. Fixed by building React app on VM and copying to Caddy volume.
3. **Caddyfile routing** — was proxying to non-existent frontend container. Fixed by changing to serve static files from `/srv`.
4. **Enum values in SQL** — used lowercase instead of uppercase. Fixed by using correct enum literals (`MEDIUM`, `HIGH`, `URGENT`).

---

## TA Demo walkthrough

1. TA navigates to `http://localhost:8080`
2. TA enters API key: `dev-api-key-change-in-production`
3. TA sees the **Task List** view with 12 assignments sorted by priority
4. Each task shows:
   - Title, course, deadline
   - Priority score (higher = more urgent)
   - Risk level color (red=critical, orange=high, yellow=medium, green=low)
   - Recommendation: "Start with Physics lab — it's worth 20% and due in 2 days"
5. TA switches to **Dashboard** view and sees:
   - Overall completion percentage
   - Per-course progress bars
   - Status distribution chart
6. TA can verify the API at `http://localhost:8080/docs` (Swagger UI)

---

## TA Feedback Points (to address in Version 2)

> These are anticipated feedback points based on the current implementation. Actual TA feedback will be incorporated during the lab session.

1. **No calendar view** — deadlines shown only as text, not visually on a calendar
2. **No ability to create/edit tasks through UI** — data must be inserted via API/SQL
3. **No conflict warnings visible in UI** — API returns them but frontend doesn't display them prominently
4. **No authentication per user** — single shared API key, no user accounts
5. **Agent (Nanobot) not actively running** — requires LLM provider configuration

These points will be addressed in Version 2.

---

## Files and structure

```
deadline-optimizer/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/__init__.py   # SQLModel: Course, Assignment, Deadline
│   │   ├── routers/             # API route handlers
│   │   │   ├── courses.py
│   │   │   ├── assignments.py
│   │   │   ├── deadlines.py
│   │   │   └── analytics.py     # Core prioritization feature
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── auth.py              # Bearer token verification
│   │   ├── main.py              # FastAPI app
│   │   └── run.py               # Uvicorn entry point
│   └── tests/
│       ├── unit/                # Unit tests
│       └── e2e/                 # E2E tests
├── client-web-react/         # React frontend
│   └── src/
│       ├── App.tsx            # Main app + task list
│       ├── Dashboard.tsx      # Charts and analytics
│       └── App.css            # Styles
├── mcp/deadline_mcp/         # MCP server for agent
│   └── server.py              # 7 MCP tools
├── nanobot/                  # AI agent config
│   ├── config.json
│   └── entrypoint.py
├── caddy/Caddyfile           # Reverse proxy
├── otel-collector/config.yaml # Observability
├── docker-compose.yml        # Service orchestration
└── version-plan.md           # V1/V2 plan (this document set)
```

---

## How to run

```bash
cd ~/deadline-optimizer
docker compose up -d
```

Then open `http://localhost:8080` and enter API key: `dev-api-key-change-in-production`
