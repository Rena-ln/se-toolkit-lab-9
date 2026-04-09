from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_session
from app.models import Course, Assignment, Deadline, PriorityLevel, AssignmentStatus
from app.schemas import (
    TaskPrioritizationRequest,
    TaskPrioritizationResponse,
    PrioritizedTask,
    CourseProgress,
    ProgressOverviewResponse,
    ConflictDetectionResponse,
    ConflictWarning,
    AssignmentResponse,
    DeadlineResponse,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def compute_priority_score(
    assignment: Assignment, deadline: Deadline, now: datetime
) -> tuple[float, str]:
    """
    Compute priority score based on urgency, weight, and status.
    Returns (score, risk_level).
    Higher score = more urgent.
    """
    days_until_due = (deadline.due_date - now).total_seconds() / 86400

    # Base score from weight (heavier assignments = higher priority)
    score = assignment.weight * 2

    # Urgency factor (closer deadlines = higher score)
    if days_until_due < 0:
        score += 100  # Overdue
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

    # Priority level multiplier
    priority_multipliers = {
        PriorityLevel.LOW: 0.5,
        PriorityLevel.MEDIUM: 1.0,
        PriorityLevel.HIGH: 1.5,
        PriorityLevel.URGENT: 2.0,
    }
    score *= priority_multipliers.get(assignment.priority, 1.0)

    # Status adjustment
    if assignment.status == AssignmentStatus.COMPLETED:
        score = 0
        risk = "low"
    elif assignment.status == AssignmentStatus.IN_PROGRESS:
        score *= 1.2  # Already started, push to finish

    return round(score, 2), risk


def generate_recommendation(
    assignment: Assignment, deadline: Deadline, score: float, risk: str, now: datetime
) -> str:
    """Generate a human-readable recommendation for the task."""
    days_until_due = (deadline.due_date - now).total_seconds() / 86400

    if assignment.status == AssignmentStatus.COMPLETED:
        return f"✅ {assignment.title} is already completed. Great job!"

    if days_until_due < 0:
        return f"🚨 OVERDUE by {abs(int(days_until_due))} days! Submit {assignment.title} immediately!"

    if days_until_due < 1:
        return f"🔥 Due in less than a day! Drop everything and work on {assignment.title} ({assignment.weight}% of grade)."

    if days_until_due < 2:
        return f"⚠️ Due tomorrow! Start with {assignment.title} — it's urgent and worth {assignment.weight}%."

    if risk == "high":
        return f"📋 {assignment.title} is due in {int(days_until_due)} days. Prioritize this — it's worth {assignment.weight}% and has high urgency."

    if risk == "medium":
        return f"📅 {assignment.title} is due in {int(days_until_due)} days. Plan to start soon — worth {assignment.weight}%."

    return f"🗓️ {assignment.title} is due in {int(days_until_due)} days. You have time, but don't forget it's worth {assignment.weight}%."


@router.post("/prioritize", response_model=TaskPrioritizationResponse)
async def prioritize_tasks(
    request: TaskPrioritizationRequest, session: AsyncSession = Depends(get_session)
):
    """
    AI-powered task prioritization.
    Analyzes all pending assignments and returns them ordered by priority score,
    with recommendations and conflict warnings.
    """
    now = datetime.now(tz=timezone.utc)

    # Build query
    query = (
        select(Assignment, Deadline)
        .join(Deadline, Assignment.id == Deadline.assignment_id)
        .join(Course, Assignment.course_id == Course.id)
        .where(Deadline.is_final == True)
        .where(Assignment.status != AssignmentStatus.COMPLETED)
        .order_by(Deadline.due_date)
    )

    if request.course_ids:
        query = query.where(Assignment.course_id.in_(request.course_ids))

    result = await session.execute(query)
    rows = result.all()

    # Compute priority scores
    prioritized_tasks = []
    for assignment, deadline in rows:
        score, risk = compute_priority_score(assignment, deadline, now)
        recommendation = generate_recommendation(assignment, deadline, score, risk, now)

        # Check for conflicts (handled separately below)
        conflicts = []

        assignment_resp = AssignmentResponse.model_validate(assignment)
        deadline_resp = DeadlineResponse.model_validate(deadline)

        prioritized_tasks.append(
            PrioritizedTask(
                assignment=assignment_resp,
                deadline=deadline_resp,
                priority_score=score,
                recommendation=recommendation,
                risk_level=risk,
                conflict_warnings=conflicts,
            )
        )

    # Sort by priority score descending
    prioritized_tasks.sort(key=lambda x: x.priority_score, reverse=True)

    # Limit results
    prioritized_tasks = prioritized_tasks[: request.max_tasks]

    # Count total pending
    total_query = select(func.count(Assignment.id)).where(
        Assignment.status != AssignmentStatus.COMPLETED
    )
    total_result = await session.execute(total_query)
    total_pending = total_result.scalar() or 0

    return TaskPrioritizationResponse(
        tasks=prioritized_tasks,
        generated_at=now,
        total_pending=total_pending,
    )


@router.get("/progress", response_model=ProgressOverviewResponse)
async def get_progress_overview(session: AsyncSession = Depends(get_session)):
    """Get per-course progress tracking and overall completion stats."""
    # Get all courses
    courses_result = await session.execute(select(Course).order_by(Course.code))
    courses = courses_result.scalars().all()

    course_progress_list = []
    total_assignments = 0
    total_completed = 0

    for course in courses:
        # Get assignments for this course
        assign_result = await session.execute(
            select(Assignment).where(Assignment.course_id == course.id)
        )
        assignments = assign_result.scalars().all()

        completed = sum(1 for a in assignments if a.status == AssignmentStatus.COMPLETED)
        in_progress = sum(1 for a in assignments if a.status == AssignmentStatus.IN_PROGRESS)
        not_started = sum(1 for a in assignments if a.status == AssignmentStatus.NOT_STARTED)
        overdue = sum(1 for a in assignments if a.status == AssignmentStatus.OVERDUE)

        course_total = len(assignments)
        percentage = round((completed / course_total * 100) if course_total > 0 else 0, 1)

        course_progress_list.append(
            CourseProgress(
                course_id=course.id,
                course_name=course.name,
                course_code=course.code,
                total_assignments=course_total,
                completed=completed,
                in_progress=in_progress,
                not_started=not_started,
                overdue=overdue,
                completion_percentage=percentage,
            )
        )

        total_assignments += course_total
        total_completed += completed

    overall_percentage = (
        round((total_completed / total_assignments * 100) if total_assignments > 0 else 0, 1)
    )

    return ProgressOverviewResponse(
        courses=course_progress_list,
        total_assignments=total_assignments,
        total_completed=total_completed,
        overall_completion_percentage=overall_percentage,
    )


@router.get("/conflicts", response_model=ConflictDetectionResponse)
async def detect_conflicts(
    window_days: int = 7, session: AsyncSession = Depends(get_session)
):
    """Detect overlapping deadlines within a time window."""
    now = datetime.now(tz=timezone.utc)
    future_date = now + timedelta(days=window_days)

    # Get all upcoming deadlines
    result = await session.execute(
        select(Deadline, Assignment)
        .join(Assignment, Deadline.assignment_id == Assignment.id)
        .where(Deadline.due_date >= now)
        .where(Deadline.due_date <= future_date)
        .where(Deadline.is_final == True)
        .order_by(Deadline.due_date)
    )
    deadlines = result.all()

    conflicts = []
    for i, (deadline1, assign1) in enumerate(deadlines):
        for deadline2, assign2 in deadlines[i + 1 :]:
            days_between = abs(
                (deadline2.due_date - deadline1.due_date).total_seconds() / 86400
            )

            if days_between <= 1:  # Due on same or consecutive days
                severity = "critical" if days_between <= 0.5 else "warning"
                conflicts.append(
                    ConflictWarning(
                        assignment_1=AssignmentResponse.model_validate(assign1),
                        deadline_1=DeadlineResponse.model_validate(deadline1),
                        assignment_2=AssignmentResponse.model_validate(assign2),
                        deadline_2=DeadlineResponse.model_validate(deadline2),
                        days_between=int(days_between),
                        severity=severity,
                    )
                )

    return ConflictDetectionResponse(conflicts=conflicts, window_days=window_days)


@router.get("/productivity", response_model=dict)
async def get_productivity_stats(session: AsyncSession = Depends(get_session)):
    """Get completed task history and productivity stats."""
    now = datetime.now(tz=timezone.utc)

    # Total completed
    completed_result = await session.execute(
        select(func.count(Assignment.id)).where(
            Assignment.status == AssignmentStatus.COMPLETED
        )
    )
    total_completed = completed_result.scalar() or 0

    # Completed this week
    week_ago = now - timedelta(days=7)
    completed_week_result = await session.execute(
        select(func.count(Assignment.id)).where(
            Assignment.status == AssignmentStatus.COMPLETED,
            Assignment.updated_at >= week_ago,
        )
    )
    completed_this_week = completed_week_result.scalar() or 0

    # Average weight of completed assignments
    avg_weight_result = await session.execute(
        select(func.avg(Assignment.weight)).where(
            Assignment.status == AssignmentStatus.COMPLETED
        )
    )
    avg_weight = round(avg_weight_result.scalar() or 0, 1)

    # Assignments by type (completed)
    type_result = await session.execute(
        select(Assignment.assignment_type, func.count(Assignment.id))
        .where(Assignment.status == AssignmentStatus.COMPLETED)
        .group_by(Assignment.assignment_type)
    )
    by_type = {row[0]: row[1] for row in type_result.all()}

    return {
        "total_completed": total_completed,
        "completed_this_week": completed_this_week,
        "average_assignment_weight": avg_weight,
        "completed_by_type": by_type,
    }
