from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_session
from app.models import Deadline, Assignment
from app.schemas import DeadlineCreate, DeadlineResponse

router = APIRouter(prefix="/deadlines", tags=["deadlines"])


@router.get("/", response_model=List[DeadlineResponse])
async def list_deadlines(
    assignment_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    """List all deadlines, optionally filtered by assignment."""
    query = select(Deadline)
    if assignment_id:
        query = query.where(Deadline.assignment_id == assignment_id)
    result = await session.execute(query.order_by(Deadline.due_date))
    deadlines = result.scalars().all()
    return deadlines


@router.get("/{deadline_id}", response_model=DeadlineResponse)
async def get_deadline(
    deadline_id: int, session: AsyncSession = Depends(get_session)
):
    """Get a specific deadline by ID."""
    result = await session.execute(
        select(Deadline).where(Deadline.id == deadline_id)
    )
    deadline = result.scalar_one_or_none()
    if not deadline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    return deadline


@router.post("/", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline(
    deadline_data: DeadlineCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new deadline."""
    # Verify assignment exists
    result = await session.execute(
        select(Assignment).where(Assignment.id == deadline_data.assignment_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
        )

    deadline = Deadline(**deadline_data.model_dump())
    session.add(deadline)
    await session.flush()
    await session.refresh(deadline)
    return deadline


@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deadline(
    deadline_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete a deadline."""
    result = await session.execute(
        select(Deadline).where(Deadline.id == deadline_id)
    )
    deadline = result.scalar_one_or_none()
    if not deadline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")

    await session.delete(deadline)
    await session.flush()
    return None
