"""MCP Server for Assignment Deadline Optimizer.

Provides tools for the AI agent to interact with the deadline optimizer API.
"""

import os
from datetime import datetime
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Create MCP server
mcp = FastMCP(
    "deadline-optimizer",
    version="0.1.0",
)

# Configuration
API_BASE_URL = os.getenv("DO_API_BASE_URL", "http://backend:8000/api/v1")
API_KEY = os.getenv("DO_API_KEY", "dev-api-key-change-in-production")


def get_headers() -> dict[str, str]:
    """Get authentication headers."""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


@mcp.tool()
async def get_prioritized_tasks(max_tasks: int = Field(default=10, description="Maximum number of tasks to return")) -> str:
    """Get AI-prioritized list of assignments ordered by urgency and importance.
    
    Use this to understand what to work on first and get personalized recommendations.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/analytics/prioritize",
            headers=get_headers(),
            json={"max_tasks": max_tasks},
        )
        response.raise_for_status()
        data = response.json()
        
    # Format as human-readable text
    lines = ["📋 PRIORITIZED TASK LIST", "=" * 50, ""]
    
    for i, task in enumerate(data.get("tasks", []), 1):
        assignment = task["assignment"]
        deadline = task["deadline"]
        
        lines.append(f"{i}. {assignment['title']}")
        lines.append(f"   Course ID: {assignment['course_id']}")
        lines.append(f"   Type: {assignment['assignment_type']}")
        lines.append(f"   Weight: {assignment['weight']}% of grade")
        lines.append(f"   Status: {assignment['status']}")
        lines.append(f"   Due: {deadline['due_date']}")
        lines.append(f"   Priority Score: {task['priority_score']}")
        lines.append(f"   Risk Level: {task['risk_level']}")
        lines.append(f"   💡 {task['recommendation']}")
        lines.append("")
    
    lines.append(f"Total pending: {data.get('total_pending', 0)}")
    lines.append(f"Generated: {data.get('generated_at', '')}")
    
    return "\n".join(lines)


@mcp.tool()
async def get_courses() -> str:
    """List all available courses with their details."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/courses/",
            headers=get_headers(),
        )
        response.raise_for_status()
        courses = response.json()
    
    lines = ["📚 COURSE CATALOG", "=" * 50, ""]
    
    for course in courses:
        lines.append(f"• {course['code']}: {course['name']}")
        if course.get('instructor'):
            lines.append(f"  Instructor: {course['instructor']}")
        lines.append(f"  Credits: {course['credits']}")
        lines.append(f"  Semester: {course['semester']}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
async def get_assignments(course_id: Optional[int] = Field(default=None, description="Filter by course ID")) -> str:
    """List all assignments, optionally filtered by course."""
    params = {}
    if course_id:
        params["course_id"] = course_id
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/assignments/",
            headers=get_headers(),
            params=params,
        )
        response.raise_for_status()
        assignments = response.json()
    
    lines = ["📝 ASSIGNMENTS", "=" * 50, ""]
    
    for assign in assignments:
        status_emoji = {
            "not_started": "⬜",
            "in_progress": "🔄",
            "submitted": "📤",
            "completed": "✅",
            "overdue": "🚨",
        }.get(assign["status"], "❓")
        
        lines.append(f"{status_emoji} {assign['title']}")
        lines.append(f"   Course: {assign['course_id']}")
        lines.append(f"   Type: {assign['assignment_type']}")
        lines.append(f"   Weight: {assign['weight']}%")
        lines.append(f"   Status: {assign['status']}")
        if assign.get("estimated_hours"):
            lines.append(f"   Est. Time: {assign['estimated_hours']}h")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
async def get_progress_overview() -> str:
    """Get overall progress across all courses with completion statistics."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/analytics/progress",
            headers=get_headers(),
        )
        response.raise_for_status()
        data = response.json()
    
    lines = ["📊 PROGRESS OVERVIEW", "=" * 50, ""]
    lines.append(f"Overall Completion: {data['overall_completion_percentage']}%")
    lines.append(f"Total Assignments: {data['total_assignments']}")
    lines.append(f"Completed: {data['total_completed']}")
    lines.append("")
    
    for course in data.get("courses", []):
        lines.append(f"📚 {course['course_code']}: {course['course_name']}")
        lines.append(f"   Completion: {course['completion_percentage']}%")
        lines.append(f"   Completed: {course['completed']}/{course['total_assignments']}")
        lines.append(f"   In Progress: {course['in_progress']}")
        lines.append(f"   Not Started: {course['not_started']}")
        if course['overdue'] > 0:
            lines.append(f"   ⚠️ Overdue: {course['overdue']}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
async def get_deadline_conflicts(window_days: int = Field(default=7, description="Number of days to look ahead")) -> str:
    """Detect overlapping deadlines within a time window to identify potential conflicts."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/analytics/conflicts",
            headers=get_headers(),
            params={"window_days": window_days},
        )
        response.raise_for_status()
        data = response.json()
    
    conflicts = data.get("conflicts", [])
    
    if not conflicts:
        return f"✅ No deadline conflicts detected in the next {window_days} days!"
    
    lines = ["⚠️ DEADLINE CONFLICTS DETECTED", "=" * 50, ""]
    
    for conflict in conflicts:
        severity = conflict["severity"].upper()
        lines.append(f"[{severity}] Overlapping deadlines:")
        lines.append(f"  • {conflict['assignment_1']['title']}")
        lines.append(f"  • {conflict['assignment_2']['title']}")
        lines.append(f"  Days between: {conflict['days_between']}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
async def get_productivity_stats() -> str:
    """Get productivity statistics including completed tasks and performance metrics."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}/analytics/productivity",
            headers=get_headers(),
        )
        response.raise_for_status()
        data = response.json()
    
    lines = ["📈 PRODUCTIVITY STATISTICS", "=" * 50, ""]
    lines.append(f"Total Completed: {data['total_completed']}")
    lines.append(f"Completed This Week: {data['completed_this_week']}")
    lines.append(f"Average Assignment Weight: {data['average_assignment_weight']}%")
    lines.append("")
    
    if data.get("completed_by_type"):
        lines.append("Completed by Type:")
        for assign_type, count in data["completed_by_type"].items():
            lines.append(f"  • {assign_type}: {count}")
    
    return "\n".join(lines)


@mcp.tool()
async def update_assignment_status(
    assignment_id: int = Field(description="Assignment ID to update"),
    status: str = Field(description="New status: not_started, in_progress, submitted, completed, overdue"),
) -> str:
    """Update the status of an assignment."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{API_BASE_URL}/assignments/{assignment_id}",
            headers=get_headers(),
            json={"status": status},
        )
        response.raise_for_status()
        data = response.json()
    
    return f"✅ Updated assignment '{data['title']}' status to: {status}"


# Export for running
def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
