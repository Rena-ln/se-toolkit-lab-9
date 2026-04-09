from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_session
from app.models import Assignment, Course
from app.schemas import AssignmentCreate, AssignmentUpdate, AssignmentResponse

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("/", response_model=List[AssignmentResponse])
async def list_assignments(
    course_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List all assignments, optionally filtered by course."""
    query = select(Assignment)
    if course_id:
        query = query.where(Assignment.course_id == course_id)
    result = await session.execute(query.order_by(Assignment.created_at.desc()))
    assignments = result.scalars().all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: int, session: AsyncSession = Depends(get_session)
):
    """Get a specific assignment by ID."""
    result = await session.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    return assignment


@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new assignment."""
    # Verify course exists
    result = await session.execute(select(Course).where(Course.id == assignment_data.course_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    assignment = Assignment(**assignment_data.model_dump())
    session.add(assignment)
    await session.flush()
    await session.refresh(assignment)
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing assignment."""
    result = await session.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    update_data = assignment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)

    await session.flush()
    await session.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete an assignment and its deadlines."""
    result = await session.execute(
        select(Assignment).where(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    await session.delete(assignment)
    await session.flush()
    return None
