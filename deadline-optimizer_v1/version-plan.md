# Assignment Deadline Optimizer — Version Plan

## Product Overview

**Product Name:** Assignment Deadline Optimizer  
**End User:** University students managing multiple courses, assignments, and exams each semester  
**Problem:** Students face 4–5 overlapping deadlines every week, don't know where to start, panic, and end up submitting late or producing low-quality work.  
**Product Idea (one sentence):** AI-powered personal deadline tracker that analyzes your workload, prioritizes tasks by urgency and complexity, and tells you exactly what to work on and when.  
**Core Feature:** AI-powered task prioritization — the agent doesn't just display deadlines, it builds a personalized action plan based on urgency, assignment weight, estimated effort, and past performance.

---

## Version 1 — Priority Engine (one core thing done well)

**Goal:** A functioning product that answers the question "What should I work on right now?"

### What Version 1 does

1. **Manage courses, assignments, and deadlines** through REST API
   - CRUD for courses, assignments, deadlines
   - Data model: courses → assignments → deadlines → status
2. **AI-powered task prioritization** — the single core feature
   - Algorithm computes priority score based on:
     - Days until deadline (urgency)
     - Assignment weight as % of final grade (importance)
     - Current status (not started, in progress, overdue)
     - Priority level (low, medium, high, urgent)
   - Returns sorted task list with human-readable recommendations
3. **React dashboard** — end-user client
   - Prioritized task list with color-coded urgency
   - Personalized recommendations ("Start with Physics lab — it's worth 20% and due tomorrow")
   - Per-course progress tracking with completion percentages
   - Status distribution chart (completed, in progress, not started, overdue)
4. **Nanobot AI agent** with MCP tools
   - Agent can query prioritized tasks, courses, assignments, progress
   - Agent detects deadline conflicts and warns user
   - Natural language interface via web chat

### Technical stack (Version 1)

| Component | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy (async) + PostgreSQL |
| Frontend | React + TypeScript + Vite + Chart.js |
| Agent | Nanobot + MCP (Model Context Protocol) |
| Database | PostgreSQL 17 |
| Reverse proxy | Caddy |
| Containerization | Docker Compose |
| Observability | OpenTelemetry + VictoriaLogs + VictoriaTraces |

### How to demonstrate Version 1 to TA

1. TA opens `http://localhost:8080` in browser
2. TA enters API key and sees the dashboard
3. TA sees a prioritized list of tasks with recommendations
4. TA can ask the agent: "What should I work on first?" and get a reasoned answer
5. TA tries updating an assignment status and sees the priority list update

### Version 1 completion criteria

- [x] Backend running with courses, assignments, deadlines endpoints
- [x] Prioritization algorithm returning scored, ordered tasks with recommendations
- [x] React SPA showing task list and progress dashboard
- [x] All services containerized via Docker Compose
- [x] Sample data loaded (5 courses, 12 assignments, 12 deadlines)
- [x] API accessible at `/api/v1/` through Caddy proxy
- [x] TA can interact with the product as a user

---

## Version 2 — Full Planner (builds upon Version 1)

**Goal:** Address TA feedback, add conflict detection UI, deploy for everyday use.

### What Version 2 adds

1. **Conflict detection visualization**
   - Visual warnings for overlapping deadlines (e.g., two exams on the same day)
   - Severity indicators (warning / critical)
2. **Conflict warnings** endpoint already exists in V1 API — needs UI display
3. **Improved frontend**
   - Calendar view of deadlines
   - Ability to create/edit courses and assignments through UI
   - Assignment status update buttons directly from task cards
4. **Polished agent recommendations**
   - Agent proactively warns about upcoming conflicts
   - Agent suggests a weekly study plan
5. **Deployed and accessible**
   - Push all code to GitHub repository `se-toolkit-hackathon`
   - MIT license
   - Full README with deployment instructions
6. **Testing and quality**
   - Unit tests for priority scoring algorithm
   - E2E tests for API endpoints
   - Type checking with Pyright
   - Linting with Ruff

### Version 2 completion criteria

- [ ] Conflict warnings displayed in UI
- [ ] Calendar view implemented
- [ ] CRUD operations available through UI (not just API)
- [ ] All tests passing
- [ ] Code published on GitHub
- [ ] Documentation complete (README.md)

---

## Architecture (both versions)

```
[Browser] -- React SPA --> Caddy --> Backend (FastAPI) --> PostgreSQL
                                                     |
[Nanobot Agent] <-- MCP stdio --> Deadline MCP Server
                      |
                      +--> LLM Provider (Qwen Code API)
                      +--> Observability: VictoriaLogs / VictoriaTraces
                                         (via OTel Collector)
```

## API Endpoints (Version 1)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/courses/` | List all courses |
| GET | `/api/v1/courses/{id}` | Get course by ID |
| POST | `/api/v1/courses/` | Create course |
| PUT | `/api/v1/courses/{id}` | Update course |
| DELETE | `/api/v1/courses/{id}` | Delete course |
| GET | `/api/v1/assignments/` | List assignments (filter by course) |
| GET | `/api/v1/assignments/{id}` | Get assignment by ID |
| POST | `/api/v1/assignments/` | Create assignment |
| PUT | `/api/v1/assignments/{id}` | Update assignment |
| DELETE | `/api/v1/assignments/{id}` | Delete assignment |
| GET | `/api/v1/deadlines/` | List deadlines (filter by assignment) |
| POST | `/api/v1/deadlines/` | Create deadline |
| DELETE | `/api/v1/deadlines/{id}` | Delete deadline |
| POST | `/api/v1/analytics/prioritize` | **Core feature** — AI-prioritized task list |
| GET | `/api/v1/analytics/progress` | Progress overview per course |
| GET | `/api/v1/analytics/conflicts` | Deadline conflict detection |
| GET | `/api/v1/analytics/productivity` | Productivity statistics |
| GET | `/health` | Health check |
