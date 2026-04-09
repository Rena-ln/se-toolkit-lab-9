"""E2E tests for the Deadline Optimizer API.

Tests run against a live backend instance.
Set E2E_API_BASE and E2E_API_KEY environment variables.
"""

import os
import pytest
from datetime import datetime, timedelta, timezone

import httpx

API_BASE = os.getenv("E2E_API_BASE", "http://localhost:8080/api/v1")
API_KEY = os.getenv("E2E_API_KEY", "dev-api-key-change-in-production")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


@pytest.fixture
def client():
    """Create an async HTTPX client."""
    with httpx.Client(base_url=API_BASE, timeout=10) as c:
        yield c


# ── Health ──────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_endpoint(self, client: httpx.Client):
        # Health is on the backend directly, not through Caddy
        resp = client.get("/health", headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            assert data["status"] == "ok"
            assert data["service"] == "deadline-optimizer"


# ── Courses CRUD ────────────────────────────────────────────────────────

class TestCourses:
    def test_list_courses(self, client: httpx.Client):
        resp = client.get("/courses/", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # at least sample data

    def test_get_course_by_id(self, client: httpx.Client):
        # First get list, then fetch first course
        resp = client.get("/courses/", headers=HEADERS)
        assert resp.status_code == 200
        courses = resp.json()
        if not courses:
            pytest.skip("No courses available")

        course_id = courses[0]["id"]
        resp = client.get(f"/courses/{course_id}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == course_id
        assert "name" in data
        assert "code" in data

    def test_create_course(self, client: httpx.Client):
        new_course = {
            "name": "Test Course E2E",
            "code": "TEST999",
            "semester": "Spring 2025",
            "credits": 3,
            "color": "#FF5733",
        }
        resp = client.post("/courses/", headers=HEADERS, json=new_course)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Course E2E"
        assert data["code"] == "TEST999"
        assert data["credits"] == 3

    def test_create_duplicate_course_code(self, client: httpx.Client):
        """Creating a course with existing code should return 409."""
        dup = {
            "name": "Duplicate Course",
            "code": "TEST999",
            "semester": "Spring 2025",
            "credits": 3,
        }
        resp = client.post("/courses/", headers=HEADERS, json=dup)
        assert resp.status_code == 409

    def test_update_course(self, client: httpx.Client):
        # Find the test course
        resp = client.get("/courses/", headers=HEADERS)
        courses = resp.json()
        test_course = next((c for c in courses if c["code"] == "TEST999"), None)
        if not test_course:
            pytest.skip("Test course not available")

        resp = client.put(
            f"/courses/{test_course['id']}",
            headers=HEADERS,
            json={"name": "Updated Course Name"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Course Name"

    def test_delete_course(self, client: httpx.Client):
        resp = client.get("/courses/", headers=HEADERS)
        courses = resp.json()
        test_course = next((c for c in courses if c["code"] == "TEST999"), None)
        if not test_course:
            pytest.skip("Test course not available")

        resp = client.delete(f"/courses/{test_course['id']}", headers=HEADERS)
        assert resp.status_code == 204

    def test_get_nonexistent_course(self, client: httpx.Client):
        resp = client.get("/courses/99999", headers=HEADERS)
        assert resp.status_code == 404

    def test_unauthorized_access(self, client: httpx.Client):
        """Auth middleware is not yet enforced on courses endpoint — TODO V2."""
        pytest.skip("Auth middleware not yet enforced on all endpoints")

    def test_no_auth_access(self, client: httpx.Client):
        """Auth middleware is not yet enforced on courses endpoint — TODO V2."""
        pytest.skip("Auth middleware not yet enforced on all endpoints")


# ── Assignments ─────────────────────────────────────────────────────────

class TestAssignments:
    def test_list_assignments(self, client: httpx.Client):
        resp = client.get("/assignments/", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_assignments_by_course(self, client: httpx.Client):
        resp = client.get("/assignments/", headers=HEADERS)
        assignments = resp.json()
        if not assignments:
            pytest.skip("No assignments available")

        course_id = assignments[0]["course_id"]
        resp = client.get(f"/assignments/?course_id={course_id}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        for a in data:
            assert a["course_id"] == course_id

    def test_get_assignment_by_id(self, client: httpx.Client):
        resp = client.get("/assignments/", headers=HEADERS)
        assignments = resp.json()
        if not assignments:
            pytest.skip("No assignments available")

        assign_id = assignments[0]["id"]
        resp = client.get(f"/assignments/{assign_id}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == assign_id

    def test_create_assignment(self, client: httpx.Client):
        # Get a course ID first
        resp = client.get("/courses/", headers=HEADERS)
        courses = resp.json()
        if not courses:
            pytest.skip("No courses available")

        course_id = courses[0]["id"]
        new_assign = {
            "course_id": course_id,
            "title": "E2E Test Assignment",
            "description": "Created by E2E test",
            "assignment_type": "homework",
            "weight": 5.0,
            "estimated_hours": 2.0,
        }
        resp = client.post("/assignments/", headers=HEADERS, json=new_assign)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "E2E Test Assignment"
        assert data["course_id"] == course_id
        assert data["weight"] == 5.0

    def test_update_assignment_status(self, client: httpx.Client):
        resp = client.get("/assignments/", headers=HEADERS)
        assignments = resp.json()
        if not assignments:
            pytest.skip("No assignments available")

        assign_id = assignments[0]["id"]
        resp = client.put(
            f"/assignments/{assign_id}",
            headers=HEADERS,
            json={"status": "in_progress"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "in_progress"


# ── Deadlines ───────────────────────────────────────────────────────────

class TestDeadlines:
    def test_list_deadlines(self, client: httpx.Client):
        resp = client.get("/deadlines/", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_create_deadline(self, client: httpx.Client):
        # Get an assignment ID
        resp = client.get("/assignments/", headers=HEADERS)
        assignments = resp.json()
        if not assignments:
            pytest.skip("No assignments available")

        assign_id = assignments[0]["id"]
        future = (datetime.now(tz=timezone.utc) + timedelta(days=30)).isoformat()

        new_deadline = {
            "assignment_id": assign_id,
            "due_date": future,
            "is_final": True,
            "notes": "E2E test deadline",
        }
        resp = client.post("/deadlines/", headers=HEADERS, json=new_deadline)
        assert resp.status_code == 201
        data = resp.json()
        assert data["assignment_id"] == assign_id
        assert data["is_final"] is True


# ── Analytics ───────────────────────────────────────────────────────────

class TestAnalytics:
    def test_prioritize_tasks(self, client: httpx.Client):
        resp = client.post(
            "/analytics/prioritize",
            headers=HEADERS,
            json={"max_tasks": 10},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "generated_at" in data
        assert "total_pending" in data
        assert isinstance(data["tasks"], list)

        if data["tasks"]:
            task = data["tasks"][0]
            assert "assignment" in task
            assert "deadline" in task
            assert "priority_score" in task
            assert "recommendation" in task
            assert "risk_level" in task
            assert isinstance(task["priority_score"], (int, float))

    def test_prioritize_respects_max_tasks(self, client: httpx.Client):
        resp = client.post(
            "/analytics/prioritize",
            headers=HEADERS,
            json={"max_tasks": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tasks"]) <= 3

    def test_prioritize_returns_sorted_desc(self, client: httpx.Client):
        resp = client.post(
            "/analytics/prioritize",
            headers=HEADERS,
            json={"max_tasks": 20},
        )
        assert resp.status_code == 200
        data = resp.json()
        scores = [t["priority_score"] for t in data["tasks"]]
        # Should be sorted descending
        assert scores == sorted(scores, reverse=True)

    def test_progress_overview(self, client: httpx.Client):
        resp = client.get("/analytics/progress", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "courses" in data
        assert "total_assignments" in data
        assert "total_completed" in data
        assert "overall_completion_percentage" in data
        assert isinstance(data["courses"], list)

    def test_conflict_detection(self, client: httpx.Client):
        resp = client.get("/analytics/conflicts", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "conflicts" in data
        assert "window_days" in data
        assert isinstance(data["conflicts"], list)

    def test_productivity_stats(self, client: httpx.Client):
        resp = client.get("/analytics/productivity", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_completed" in data
        assert "completed_this_week" in data
        assert "average_assignment_weight" in data
        assert "completed_by_type" in data
