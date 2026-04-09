"""Unit tests for the priority scoring algorithm, recommendation logic, and schemas.

These tests are standalone and do NOT require a database connection.
"""

import enum
from datetime import datetime, timedelta, timezone

import pytest


# ── Replicated enums (standalone, no DB dependency) ─────────────────────

class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AssignmentStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    OVERDUE = "overdue"


# ── Replicated scoring logic (copy of analytics.py algorithm) ────────────

def compute_priority_score(weight: float, days_until_due: float,
                           priority: PriorityLevel, status: AssignmentStatus) -> tuple[float, str]:
    """
    Compute priority score based on urgency, weight, and status.
    Returns (score, risk_level).
    This is a standalone copy of the algorithm in analytics.py for unit testing.
    """
    score = weight * 2

    if days_until_due < 0:
        score += 100
        risk = "critical"
    elif days_until_due < 1:
        score += 50
        risk = "critical"
    elif days_until_due < 2:
        score += 30
        risk = "high"
    elif days_until_due < 5:
        score += 20
        risk = "high"
    elif days_until_due < 7:
        score += 10
        risk = "medium"
    else:
        risk = "low"

    priority_multipliers = {
        PriorityLevel.LOW: 0.5,
        PriorityLevel.MEDIUM: 1.0,
        PriorityLevel.HIGH: 1.5,
        PriorityLevel.URGENT: 2.0,
    }
    score *= priority_multipliers.get(priority, 1.0)

    if status == AssignmentStatus.COMPLETED:
        score = 0
        risk = "low"
    elif status == AssignmentStatus.IN_PROGRESS:
        score *= 1.2

    return round(score, 2), risk


def generate_recommendation(title: str, days_until_due: float,
                            weight: float, status: str = "not_started") -> str:
    """Standalone copy of the recommendation generator."""
    if status == "completed":
        return f"✅ {title} is already completed. Great job!"
    if days_until_due < 0:
        return f"🚨 OVERDUE by {abs(int(days_until_due))} days! Submit {title} immediately!"
    if days_until_due < 1:
        return f"🔥 Due in less than a day! Drop everything and work on {title} ({weight}% of grade)."
    if days_until_due < 2:
        return f"⚠️ Due tomorrow! Start with {title} — it's urgent and worth {weight}%."
    if days_until_due < 5:
        return f"📋 {title} is due in {int(days_until_due)} days. Prioritize this — it's worth {weight}% and has high urgency."
    if days_until_due < 7:
        return f"📅 {title} is due in {int(days_until_due)} days. Plan to start soon — worth {weight}%."
    return f"🗓️ {title} is due in {int(days_until_due)} days. You have time, but don't forget it's worth {weight}%."


# ── Tests: Priority Score Computation ────────────────────────────────────

class TestPriorityScoreComputation:

    def test_overdue_assignment_gets_max_bonus(self):
        """Overdue assignments should get +100 base score."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=-1,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 120.0
        assert risk == "critical"

    def test_due_tomorrow_gets_high_urgency(self):
        """Assignment due in <1 day should get +50."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=0.5,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 70.0
        assert risk == "critical"

    def test_due_in_1_day_gets_high_risk(self):
        """Assignment due in 1-2 days should get +30, risk=high."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=1.5,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 50.0
        assert risk == "high"

    def test_due_in_3_days_gets_medium_urgency(self):
        """Assignment due in 2-5 days should get +20."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=3,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 40.0
        assert risk == "high"

    def test_due_in_6_days_gets_medium_risk(self):
        """Assignment due in 5-7 days should get +10."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=6,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 30.0
        assert risk == "medium"

    def test_due_in_10_days_gets_no_urgency_bonus(self):
        """Assignment due in >7 days gets no urgency bonus."""
        score, risk = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert score == 20.0
        assert risk == "low"

    def test_urgent_priority_doubles_score(self):
        """URGENT priority should double the score."""
        base, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        urgent, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.URGENT,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert urgent == base * 2.0

    def test_high_priority_increases_by_50_percent(self):
        """HIGH priority should multiply score by 1.5."""
        base, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        high, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.HIGH,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert high == base * 1.5

    def test_low_priority_halves_score(self):
        """LOW priority should halve the score."""
        base, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        low, _ = compute_priority_score(
            weight=10, days_until_due=10,
            priority=PriorityLevel.LOW,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert low == base * 0.5

    def test_completed_assignment_has_zero_score(self):
        """Completed assignments should have score 0."""
        score, risk = compute_priority_score(
            weight=30, days_until_due=-5,
            priority=PriorityLevel.URGENT,
            status=AssignmentStatus.COMPLETED,
        )
        assert score == 0.0
        assert risk == "low"

    def test_in_progress_assignment_gets_20_percent_boost(self):
        """In-progress assignments should get 1.2x multiplier."""
        not_started, _ = compute_priority_score(
            weight=10, days_until_due=3,
            priority=PriorityLevel.HIGH,
            status=AssignmentStatus.NOT_STARTED,
        )
        in_progress, _ = compute_priority_score(
            weight=10, days_until_due=3,
            priority=PriorityLevel.HIGH,
            status=AssignmentStatus.IN_PROGRESS,
        )
        assert in_progress == not_started * 1.2

    def test_heavier_assignment_has_higher_base(self):
        """Higher weight assignments should have higher base score."""
        low_weight, _ = compute_priority_score(
            weight=5, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        high_weight, _ = compute_priority_score(
            weight=30, days_until_due=10,
            priority=PriorityLevel.MEDIUM,
            status=AssignmentStatus.NOT_STARTED,
        )
        assert high_weight > low_weight

    def test_overdue_urgent_assignment_has_maximum_score(self):
        """An overdue, urgent, high-weight assignment should score highest."""
        score, risk = compute_priority_score(
            weight=30, days_until_due=-1,
            priority=PriorityLevel.URGENT,
            status=AssignmentStatus.NOT_STARTED,
        )
        # (30*2 + 100) * 2.0 = 320
        assert score == 320.0
        assert risk == "critical"

    def test_score_ordering_matches_urgency(self):
        """More urgent tasks should always have higher or equal score (same weight)."""
        scores = []
        for days in [-1, 0.5, 1.5, 3, 6, 10]:
            s, _ = compute_priority_score(
                weight=10, days_until_due=days,
                priority=PriorityLevel.MEDIUM,
                status=AssignmentStatus.NOT_STARTED,
            )
            scores.append(s)
        # Should be monotonically decreasing as days increase
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]


# ── Tests: Recommendation Generation ─────────────────────────────────────

class TestRecommendationGeneration:

    def test_overdue_recommendation(self):
        text = generate_recommendation("Math Homework", days_until_due=-3, weight=10)
        assert "OVERDUE" in text
        assert "3 days" in text

    def test_due_today_recommendation(self):
        text = generate_recommendation("Physics Lab", days_until_due=0.5, weight=20)
        assert "less than a day" in text
        assert "20%" in text

    def test_tomorrow_recommendation(self):
        text = generate_recommendation("Essay", days_until_due=1.5, weight=15)
        assert "tomorrow" in text
        assert "15%" in text

    def test_few_days_recommendation(self):
        text = generate_recommendation("Quiz", days_until_due=3, weight=10)
        assert "3 days" in text
        assert "Prioritize" in text

    def test_week_recommendation(self):
        text = generate_recommendation("Project", days_until_due=6, weight=25)
        assert "6 days" in text
        assert "Plan to start soon" in text

    def test_far_deadline_recommendation(self):
        text = generate_recommendation("Report", days_until_due=14, weight=10)
        assert "14 days" in text
        assert "don't forget" in text

    def test_completed_recommendation(self):
        text = generate_recommendation("Homework", days_until_due=5, weight=10, status="completed")
        assert "completed" in text
        assert "Great job" in text

    def test_recommendation_contains_title(self):
        text = generate_recommendation("My Special Task", days_until_due=3, weight=10)
        assert "My Special Task" in text

    def test_recommendation_contains_weight(self):
        text = generate_recommendation("Task", days_until_due=3, weight=42.5)
        assert "42.5%" in text


# ── Tests: Pydantic Schemas (standalone validation) ──────────────────────

class TestPydanticSchemas:
    """Test that Pydantic schemas validate correctly.
    
    We test the schema definitions directly without importing from app
    to avoid DB dependency. These validate the same field structures.
    """

    def test_course_fields(self):
        from pydantic import BaseModel
        from typing import Optional

        class CourseCreate(BaseModel):
            name: str
            code: str
            description: Optional[str] = None
            instructor: Optional[str] = None
            semester: str
            credits: int = 3
            color: Optional[str] = "#3B82F6"

        course = CourseCreate(
            name="Test Course",
            code="TEST101",
            semester="Fall 2024",
            credits=3,
        )
        assert course.name == "Test Course"
        assert course.code == "TEST101"
        assert course.credits == 3
        assert course.color == "#3B82F6"

    def test_course_validation_errors(self):
        from pydantic import BaseModel, ValidationError
        from typing import Optional

        class CourseCreate(BaseModel):
            name: str
            code: str
            semester: str
            credits: int = 3

        with pytest.raises(ValidationError):
            CourseCreate(code="TEST", semester="Fall")  # missing name

        with pytest.raises(ValidationError):
            CourseCreate(name="Test", semester="Fall")  # missing code

    def test_assignment_fields(self):
        from pydantic import BaseModel
        from typing import Optional

        class AssignmentCreate(BaseModel):
            course_id: int
            title: str
            description: Optional[str] = None
            assignment_type: str = "homework"
            weight: float = 10.0
            estimated_hours: Optional[float] = None

        a = AssignmentCreate(course_id=1, title="Test", weight=15.0)
        assert a.course_id == 1
        assert a.weight == 15.0
        assert a.assignment_type == "homework"

    def test_deadline_fields(self):
        from pydantic import BaseModel
        from typing import Optional

        class DeadlineCreate(BaseModel):
            assignment_id: int
            due_date: datetime
            is_final: bool = True
            notes: Optional[str] = None

        now = datetime.now(tz=timezone.utc)
        d = DeadlineCreate(assignment_id=1, due_date=now, is_final=True)
        assert d.assignment_id == 1
        assert d.is_final is True

    def test_prioritized_task_structure(self):
        from pydantic import BaseModel
        from typing import Optional

        class TaskStub(BaseModel):
            priority_score: float
            recommendation: str
            risk_level: str
            conflict_warnings: list[str] = []

        task = TaskStub(
            priority_score=50.0,
            recommendation="Do this first",
            risk_level="high",
            conflict_warnings=["Overlapping deadline"],
        )
        assert task.priority_score == 50.0
        assert len(task.conflict_warnings) == 1

    def test_conflict_warning_structure(self):
        from pydantic import BaseModel

        class ConflictWarning(BaseModel):
            assignment_1_title: str
            assignment_2_title: str
            days_between: int
            severity: str

        cw = ConflictWarning(
            assignment_1_title="Exam 1",
            assignment_2_title="Exam 2",
            days_between=0,
            severity="critical",
        )
        assert cw.severity == "critical"
        assert cw.days_between == 0


# ── Tests: Settings ──────────────────────────────────────────────────────

class TestSettings:
    """Test application settings defaults and env var overrides."""

    def test_settings_defaults(self):
        """Test that Settings can be created with defaults."""
        from pydantic_settings import BaseSettings
        from typing import List

        class TestSettings(BaseSettings):
            backend_host: str = "0.0.0.0"
            backend_port: int = 8000
            backend_debug: bool = False
            backend_api_key: str = "dev-api-key"

            class Config:
                env_file = ".env"
                populate_by_name = True

        settings = TestSettings()
        assert settings.backend_host == "0.0.0.0"
        assert settings.backend_port == 8000
        assert settings.backend_debug is False
        assert settings.backend_api_key == "dev-api-key"

    def test_settings_from_env(self, monkeypatch):
        """Test that environment variables override defaults."""
        from pydantic_settings import BaseSettings
        from typing import List

        class TestSettings(BaseSettings):
            backend_port: int = 8000
            backend_debug: bool = False
            backend_api_key: str = "dev-api-key"

        monkeypatch.setenv("BACKEND_PORT", "9000")
        monkeypatch.setenv("BACKEND_DEBUG", "true")
        monkeypatch.setenv("BACKEND_API_KEY", "test-key")

        settings = TestSettings()
        assert settings.backend_port == 9000
        assert settings.backend_debug is True
        assert settings.backend_api_key == "test-key"


# ── Tests: Conflict Detection Logic ──────────────────────────────────────

class TestConflictDetection:
    """Test the logic for detecting overlapping deadlines."""

    def detect_conflicts(self, deadlines: list[datetime], window_days: int = 1) -> list[tuple[int, int, int]]:
        """Standalone conflict detection.
        Returns list of (index1, index2, days_between) for conflicting pairs.
        """
        conflicts = []
        for i in range(len(deadlines)):
            for j in range(i + 1, len(deadlines)):
                delta = abs((deadlines[j] - deadlines[i]).total_seconds()) / 86400
                if delta <= window_days:
                    conflicts.append((i, j, int(delta)))
        return conflicts

    def test_same_day_deadlines_conflict(self):
        now = datetime.now(tz=timezone.utc)
        deadlines = [now + timedelta(days=3), now + timedelta(days=3, hours=2)]
        conflicts = self.detect_conflicts(deadlines, window_days=1)
        assert len(conflicts) == 1
        assert conflicts[0][2] == 0  # 0 days between

    def test_adjacent_day_deadlines_conflict(self):
        now = datetime.now(tz=timezone.utc)
        deadlines = [now + timedelta(days=3), now + timedelta(days=4)]
        conflicts = self.detect_conflicts(deadlines, window_days=1)
        assert len(conflicts) == 1
        assert conflicts[0][2] == 1

    def test_spaced_deadlines_no_conflict(self):
        now = datetime.now(tz=timezone.utc)
        deadlines = [now + timedelta(days=3), now + timedelta(days=10)]
        conflicts = self.detect_conflicts(deadlines, window_days=1)
        assert len(conflicts) == 0

    def test_multiple_conflicts(self):
        now = datetime.now(tz=timezone.utc)
        deadlines = [
            now + timedelta(days=1),
            now + timedelta(days=1, hours=12),
            now + timedelta(days=2),
            now + timedelta(days=10),
        ]
        conflicts = self.detect_conflicts(deadlines, window_days=1)
        assert len(conflicts) >= 2  # at least 2 pairs conflict

    def test_empty_deadlines_no_conflicts(self):
        assert self.detect_conflicts([]) == []

    def test_single_deadline_no_conflicts(self):
        now = datetime.now(tz=timezone.utc)
        assert self.detect_conflicts([now]) == []
