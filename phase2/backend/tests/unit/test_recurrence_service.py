from uuid import UUID
from datetime import datetime, timedelta, UTC
import pytest
from sqlmodel import Session, SQLModel, create_engine
from phase2.backend.src.models import Task
from phase2.backend.src.schemas.task import TaskCreate
from phase2.backend.src.services.recurrence_service import generate_recurring_task_instance

# Setup a test database engine
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def test_generate_recurring_task_daily(session: Session):
    original_due_date = datetime.now(UTC).replace(microsecond=0) # Ensure microsecond is 0 for consistent comparison
    original_task = Task(
        title="Daily Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
        status="completed",
        priority="low",
        recurrence="daily",
        due_date=original_due_date
    )
    session.add(original_task)
    session.commit()
    session.refresh(original_task)

    new_task = generate_recurring_task_instance(session, original_task)
    assert new_task is not None
    assert new_task.title == original_task.title
    assert new_task.user_id == original_task.user_id
    assert new_task.status == "pending"
    assert new_task.recurrence == "daily"
    assert new_task.due_date.replace(tzinfo=UTC) == (original_due_date + timedelta(days=1)).replace(microsecond=0)

def test_generate_recurring_task_weekly(session: Session):
    original_due_date = datetime.now(UTC).replace(microsecond=0)
    original_task = Task(
        title="Weekly Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
        status="completed",
        priority="low",
        recurrence="weekly",
        due_date=original_due_date
    )
    session.add(original_task)
    session.commit()
    session.refresh(original_task)

    new_task = generate_recurring_task_instance(session, original_task)
    assert new_task is not None
    assert new_task.recurrence == "weekly"
    assert new_task.due_date.replace(tzinfo=UTC) == (original_due_date + timedelta(weeks=1)).replace(microsecond=0)

def test_generate_recurring_task_monthly(session: Session):
    original_due_date = datetime.now(UTC).replace(microsecond=0)
    original_task = Task(
        title="Monthly Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
        status="completed",
        priority="low",
        recurrence="monthly",
        due_date=original_due_date
    )
    session.add(original_task)
    session.commit()
    session.refresh(original_task)

    new_task = generate_recurring_task_instance(session, original_task)
    assert new_task is not None
    assert new_task.recurrence == "monthly"
    assert new_task.due_date.replace(tzinfo=UTC) == (original_due_date + timedelta(days=30)).replace(microsecond=0) # Simple monthly logic

def test_no_recurrence_task(session: Session):
    original_task = Task(
        title="One-time Task",
        user_id=UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),        status="completed",
        priority="low",
        recurrence=None,
        due_date=datetime.now(UTC)
    )
    session.add(original_task)
    session.commit()
    session.refresh(original_task)

    new_task = generate_recurring_task_instance(session, original_task)
    assert new_task is None