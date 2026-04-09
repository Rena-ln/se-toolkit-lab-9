from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_session
from app.models import Course
from app.schemas import CourseCreate, CourseUpdate, CourseResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=List[CourseResponse])
async def list_courses(session: AsyncSession = Depends(get_session)):
    """List all courses."""
    result = await session.execute(select(Course).order_by(Course.code))
    courses = result.scalars().all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific course by ID."""
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new course."""
    # Check if course code already exists
    result = await session.execute(select(Course).where(Course.code == course_data.code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Course code already exists"
        )

    course = Course(**course_data.model_dump())
    session.add(course)
    await session.flush()
    await session.refresh(course)
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an existing course."""
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    update_data = course_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    await session.flush()
    await session.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a course and all its assignments."""
    result = await session.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    await session.delete(course)
    await session.flush()
    return None
