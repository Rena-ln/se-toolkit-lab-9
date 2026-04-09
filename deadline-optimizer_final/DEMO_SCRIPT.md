# Demo Script — Assignment Deadline Optimizer v2

> Pre-recorded video demonstration with voice-over (target: ≤ 2 minutes)

## Script

### 0:00 – 0:15 — Introduction
"Hi, this is the Assignment Deadline Optimizer — an AI-powered tool that tells students exactly what to work on and when. Let me show you Version 2."

### 0:15 – 0:35 — Task List View
"Here's the main view. You can see all my assignments sorted by priority. The red bar means critical — the Algorithm Quiz is due tomorrow and worth 15%. Each task has a recommendation: 'Drop everything and work on this.' The score combines urgency, weight, and priority level."

### 0:35 – 0:55 — Dashboard
"Switching to the Dashboard — I can see per-course progress. CS101 has 3 assignments, none completed yet. The doughnut chart shows most tasks are not started. Overall completion is 0% — I need to get to work!"

### 0:55 – 1:25 — Manage Tab (New in v2)
"Now the Manage tab — new in Version 2. I can create a new deadline here: select the assignment, pick a date and time, add notes, and click Create. Done. I can also delete deadlines from the table below. And I can create entirely new assignments — picking a course, setting the title, type, weight, and priority."

### 1:25 – 1:45 — API and Agent
"The backend exposes a REST API. I can call the prioritize endpoint and get scored recommendations. There's also an MCP server with 7 tools so an AI agent like Nanobot can query my deadlines and give natural language advice."

### 1:45 – 2:00 — Conclusion
"This is deployed via Docker Compose with FastAPI, PostgreSQL, React frontend, and Caddy proxy. All code is open-source under MIT license. Thanks!"

---

## Recording Instructions

To record the demo:

1. Start the application: `docker compose up -d`
2. Open browser at `http://localhost:8080`
3. Enter API key: `dev-api-key-change-in-production`
4. Use OBS Studio or any screen recorder
5. Follow the script timing above
6. Save as `demo-v2.mp4`
