from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PriorityLevel(str, enum.Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AssignmentStatus(str, enum.Enum):
    """Assignment completion status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Course(Base):
    """A university course."""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructor = Column(String(255), nullable=True)
    semester = Column(String(50), nullable=False)
    credits = Column(Integer, nullable=False, default=3)
    color = Column(String(7), nullable=True, default="#3B82F6")  # Hex color for UI
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assignments = relationship("Assignment", back_populates="course", cascade="all, delete-orphan")


class Assignment(Base):
    """An assignment/task within a course."""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    assignment_type = Column(String(50), nullable=False, default="homework")  # homework, lab, exam, project, etc.
    weight = Column(Float, nullable=False, default=10.0)  # Percentage of final grade
    estimated_hours = Column(Float, nullable=True)  # Estimated effort hours
    priority = Column(Enum(PriorityLevel), nullable=False, default=PriorityLevel.MEDIUM)
    status = Column(Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.NOT_STARTED)
    attributes = Column(JSON, nullable=True)  # Extra metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="assignments")
    deadlines = relationship("Deadline", back_populates="assignment", cascade="all, delete-orphan")


class Deadline(Base):
    """A deadline for an assignment."""

    __tablename__ = "deadlines"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    is_final = Column(Boolean, nullable=False, default=True)  # False for intermediate milestones
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assignment = relationship("Assignment", back_populates="deadlines")
