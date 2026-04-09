# Assignment Deadline Optimizer

> AI-powered personal deadline tracker that analyzes your workload, prioritizes tasks by urgency and complexity, and tells you exactly what to work on and when.

## 🎯 Overview

University students face 4–5 overlapping deadlines every week, don't know where to start, panic, and end up submitting late or producing low-quality work. The **Assignment Deadline Optimizer** solves this with **AI-powered prioritization** — the agent doesn't just display deadlines, it builds a personalized action plan based on urgency, assignment weight, estimated effort, and past performance.

## 🏗️ Architecture

```
[Browser] -- React SPA --> Caddy --> Backend (FastAPI) --> PostgreSQL
                                                     |
[Nanobot Agent] <-- MCP stdio --> Deadline MCP Server
                      |
                      +--> LLM: Qwen Code API
                      +--> Observability: VictoriaLogs / VictoriaTraces
                                         (via OTel Collector)
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+ & pnpm

### 1. Clone the repository

```bash
git clone <repository-url>
cd deadline-optimizer
```

### 2. Configure environment

```bash
cp .env.docker.example .env.docker.secret
# Edit .env.docker.secret with your actual API keys
```

### 3. Start all services

```bash
docker compose up -d
```

### 4. Access the application

- **Frontend Dashboard**: http://localhost:8080
- **Backend API Docs**: http://localhost:8080/docs
- **Agent Web Chat**: http://localhost:8765
- **PgAdmin**: http://localhost:54320

## 📋 Features

### Main Features

- **Unified calendar** of all deadlines across courses
- **AI-powered task prioritization** (what to do first and why)
- **Personalized agent recommendations** ("start with Physics lab — it's the heaviest and worth 20%")
- **Conflict warnings** for overlapping deadlines
- **Per-course progress tracking**
- **Completed task history** and productivity stats

### Data Model

```
courses → assignments → deadlines → status
```

## 🛠️ Tech Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript + Vite + Chart.js
- **Agent**: Nanobot + MCP (Model Context Protocol)
- **Observability**: OpenTelemetry + VictoriaLogs + VictoriaTraces
- **Reverse Proxy**: Caddy
- **Containerization**: Docker Compose

## 📁 Project Structure

```
deadline-optimizer/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLModel definitions
│   │   ├── routers/        # API route handlers
│   │   ├── database.py     # Async SQLAlchemy setup
│   │   ├── main.py         # FastAPI app
│   │   └── run.py          # Uvicorn entry point
│   └── tests/
├── client-web-react/        # React frontend
│   └── src/
├── mcp/                     # MCP server
│   └── deadline_mcp/
├── nanobot/                 # AI agent
├── caddy/                   # Reverse proxy
├── otel-collector/          # Observability
└── docker-compose.yml       # Service orchestration
```

## 🧪 Development

### Run backend locally

```bash
cd backend
uv sync
uv run uvicorn app.run:app --reload
```

### Run frontend locally

```bash
cd client-web-react
pnpm install
pnpm dev
```

### Run tests

```bash
# Unit tests
uv run pytest backend/tests/unit -v

# E2E tests
uv run pytest backend/tests/e2e -v
```

## 👥 Target Users

University students managing multiple courses, assignments, and exams each semester.

## 📝 License

MIT License
