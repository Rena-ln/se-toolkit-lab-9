# Nanobot Agent for Assignment Deadline Optimizer

## Overview

This directory contains the Nanobot AI agent configuration for the Assignment Deadline Optimizer.

## Configuration

The agent is configured via `config.json` with environment variable resolution.

### Key Settings

- **Model**: Configured via `NANOBOT_MODEL` (default: `coder-model`)
- **Provider**: Custom LLM provider via `NANOBOT_API_BASE`
- **MCP Server**: Connected to the deadline optimizer MCP tools
- **Web Chat**: Available on port 8765

## MCP Tools

The agent has access to the following tools via MCP:

1. **get_prioritized_tasks** - Get AI-prioritized task list with recommendations
2. **get_courses** - List all courses
3. **get_assignments** - List assignments (optionally filtered by course)
4. **get_progress_overview** - Get overall progress statistics
5. **get_deadline_conflicts** - Detect overlapping deadlines
6. **get_productivity_stats** - Get productivity metrics
7. **update_assignment_status** - Update assignment completion status

## Running Locally

```bash
# Set environment variables
export NANOBOT_MODEL=coder-model
export NANOBOT_API_BASE=http://localhost:42005/v1
export QWEN_CODE_API_KEY=your-key

# Run the agent
python entrypoint.py
```

## Accessing Web Chat

Once running, access the chat interface at: http://localhost:8765
