from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models import PriorityLevel, AssignmentStatus


# Course schemas
class CourseCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    semester: str
    credits: int = 3
    color: Optional[str] = "#3B82F6"


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    semester: Optional[str] = None
    credits: Optional[int] = None
    color: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    instructor: Optional[str]
    semester: str
    credits: int
    color: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Assignment schemas
class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    assignment_type: str = "homework"
    weight: float = 10.0
    estimated_hours: Optional[float] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: AssignmentStatus = AssignmentStatus.NOT_STARTED
    attributes: Optional[dict] = None


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignment_type: Optional[str] = None
    weight: Optional[float] = None
    estimated_hours: Optional[float] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[AssignmentStatus] = None
    attributes: Optional[dict] = None


class AssignmentResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    assignment_type: str
    weight: float
    estimated_hours: Optional[float]
    priority: PriorityLevel
    status: AssignmentStatus
    attributes: Optional[dict]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Deadline schemas
class DeadlineCreate(BaseModel):
    assignment_id: int
    due_date: datetime
    is_final: bool = True
    notes: Optional[str] = None


class DeadlineResponse(BaseModel):
    id: int
    assignment_id: int
    due_date: datetime
    is_final: bool
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# Analytics schemas
class TaskPrioritizationRequest(BaseModel):
    course_ids: Optional[list[int]] = None
    max_tasks: int = Field(default=10, ge=1, le=50)


class PrioritizedTask(BaseModel):
    assignment: AssignmentResponse
    deadline: DeadlineResponse
    priority_score: float  # Computed priority score (higher = more urgent)
    recommendation: str  # AI-generated recommendation text
    risk_level: str  # "low", "medium", "high", "critical"
    conflict_warnings: list[str] = []


class TaskPrioritizationResponse(BaseModel):
    tasks: list[PrioritizedTask]
    generated_at: datetime
    total_pending: int


class CourseProgress(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    total_assignments: int
    completed: int
    in_progress: int
    not_started: int
    overdue: int
    completion_percentage: float


class ProgressOverviewResponse(BaseModel):
    courses: list[CourseProgress]
    total_assignments: int
    total_completed: int
    overall_completion_percentage: float


class ConflictWarning(BaseModel):
    assignment_1: AssignmentResponse
    deadline_1: DeadlineResponse
    assignment_2: AssignmentResponse
    deadline_2: DeadlineResponse
    days_between: int
    severity: str  # "warning", "critical"


class ConflictDetectionResponse(BaseModel):
    conflicts: list[ConflictWarning]
    window_days: int = 7
