import pytest
from sqlmodel import Session, SQLModel, create_engine
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from src.services.recurring_tasks_service import RecurringTaskService
from src.models import User, Task
from sqlalchemy.pool import StaticPool

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="recurring_service")
def recurring_service_fixture(session):
    return RecurringTaskService(session)

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        id=uuid4(),
        email="recurringtest@example.com",
        username="recurringuser",
        hashed_password="password",
        status="Active"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_daily_recurrence(recurring_service, test_user):
    now = datetime.now()
    pattern = {"frequency": "daily", "interval": 2}
    task = Task(
        title="Daily Task",
        user_id=test_user.id,
        due_date=now,
        recurrence_pattern=pattern
    )
    
    new_task = recurring_service.create_recurring_task_instance(task)
    assert new_task is not None
    assert new_task.due_date == now + timedelta(days=2)
    assert new_task.status == "pending"

def test_weekly_recurrence(recurring_service, test_user):
    now = datetime.now()
    pattern = {"frequency": "weekly", "interval": 1}
    task = Task(
        title="Weekly Task",
        user_id=test_user.id,
        due_date=now,
        recurrence_pattern=pattern
    )
    
    new_task = recurring_service.create_recurring_task_instance(task)
    assert new_task.due_date == now + timedelta(weeks=1)

def test_monthly_recurrence(recurring_service, test_user):
    # Test month end handling
    start_date = datetime(2024, 1, 31)
    pattern = {"frequency": "monthly", "interval": 1}
    task = Task(
        title="Monthly Task",
        user_id=test_user.id,
        due_date=start_date,
        recurrence_pattern=pattern
    )
    
    new_task = recurring_service.create_recurring_task_instance(task)
    # Feb 2024 is leap year, should be 29th
    assert new_task.due_date == datetime(2024, 2, 29)

def test_yearly_recurrence(recurring_service, test_user):
    start_date = datetime(2024, 1, 1)
    pattern = {"frequency": "yearly", "interval": 1}
    task = Task(
        title="Yearly Task",
        user_id=test_user.id,
        due_date=start_date,
        recurrence_pattern=pattern
    )
    
    new_task = recurring_service.create_recurring_task_instance(task)
    assert new_task.due_date == datetime(2025, 1, 1)

def test_end_condition_on_date(recurring_service, test_user):
    now = datetime.now()
    end_date = now + timedelta(days=1)
    pattern = {
        "frequency": "daily",
        "interval": 2,
        "end_condition": {"type": "on_date", "value": end_date.isoformat()}
    }
    task = Task(
        title="Ending Task",
        user_id=test_user.id,
        due_date=now,
        recurrence_pattern=pattern
    )
    
    # Should not create because next occurrence (now + 2 days) is after end_date
    new_task = recurring_service.create_recurring_task_instance(task)
    assert new_task is None

def test_reminder_calculation(recurring_service, test_user):
    due_date = datetime(2024, 1, 1, 12, 0)
    reminder = datetime(2024, 1, 1, 10, 0) # 2 hours before
    pattern = {"frequency": "daily", "interval": 1}
    
    task = Task(
        title="Reminder Task",
        user_id=test_user.id,
        due_date=due_date,
        reminder_time=reminder,
        recurrence_pattern=pattern
    )
    
    new_task = recurring_service.create_recurring_task_instance(task)
    assert new_task.due_date == datetime(2024, 1, 2, 12, 0)
    assert new_task.reminder_time == datetime(2024, 1, 2, 10, 0)

def test_process_completed_recurring_task(recurring_service, test_user, session):
    task = Task(
        title="Initial Task",
        user_id=test_user.id,
        due_date=datetime.now(),
        recurrence_pattern={"frequency": "daily"}
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    new_instance = recurring_service.process_completed_recurring_task(task.id)
    assert new_instance is not None
    assert new_instance.title == "Initial Task"
    
    # Try non-existent OR non-recurring
    assert recurring_service.process_completed_recurring_task(uuid4()) is None
    
    task.recurrence_pattern = None
    session.add(task)
    session.commit()
    assert recurring_service.process_completed_recurring_task(task.id) is None
