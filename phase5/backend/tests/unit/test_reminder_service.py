import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from src.services.reminder_service import ReminderService
from src.models import User, Task, Notification
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

@pytest.fixture(name="reminder_service")
def reminder_service_fixture(session):
    return ReminderService(session)

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        id=uuid4(),
        email="remindertest@example.com",
        username="reminderuser",
        hashed_password="password",
        status="Active"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_schedule_reminders_for_task(reminder_service, test_user, session):
    now = datetime.now()
    task = Task(
        id=uuid4(),
        title="Task 1",
        user_id=test_user.id,
        due_date=now + timedelta(days=1),
        reminder_time=now + timedelta(hours=12)
    )
    session.add(task)
    session.commit()
    
    assert reminder_service.schedule_reminders_for_task(task) is True
    
    # Check notification created
    notif = session.exec(select(Notification).where(Notification.task_id == task.id)).first()
    assert notif is not None
    assert notif.status == "scheduled"
    assert notif.scheduled_time == task.reminder_time

def test_schedule_reminders_for_user_tasks(reminder_service, test_user, session):
    now = datetime.now()
    t1 = Task(title="T1", user_id=test_user.id, due_date=now, reminder_time=now)
    t2 = Task(title="T2", user_id=test_user.id, due_date=now, reminder_time=now)
    t3 = Task(title="T3", user_id=test_user.id) # No reminder
    session.add_all([t1, t2, t3])
    session.commit()
    
    count = reminder_service.schedule_reminders_for_user_tasks(test_user.id)
    assert count == 2

def test_check_and_send_reminders(reminder_service, test_user, session):
    now = datetime.now()
    # Past reminder
    n1 = Notification(id=uuid4(), user_id=test_user.id, type="reminder", scheduled_time=now - timedelta(minutes=5), status="scheduled")
    # Future reminder
    n2 = Notification(id=uuid4(), user_id=test_user.id, type="reminder", scheduled_time=now + timedelta(minutes=5), status="scheduled")
    session.add_all([n1, n2])
    session.commit()
    
    sent_count = reminder_service.check_and_send_due_date_reminders()
    assert sent_count == 1
    
    session.refresh(n1)
    session.refresh(n2)
    assert n1.status == "sent"
    assert n2.status == "scheduled"

def test_get_upcoming_reminders(reminder_service, test_user, session):
    now = datetime.now()
    n1 = Notification(user_id=test_user.id, type="r", scheduled_time=now + timedelta(hours=1), status="scheduled")
    n2 = Notification(user_id=test_user.id, type="r", scheduled_time=now + timedelta(hours=5), status="scheduled")
    session.add_all([n1, n2])
    session.commit()
    
    upcoming = reminder_service.get_upcoming_reminders(test_user.id, hours_ahead=2)
    assert len(upcoming) == 1
    assert upcoming[0].id == n1.id

def test_cancel_reminder(reminder_service, test_user, session):
    n = Notification(user_id=test_user.id, type="r", scheduled_time=datetime.now(), status="scheduled")
    session.add(n)
    session.commit()
    session.refresh(n)
    
    assert reminder_service.cancel_reminder(n.id) is True
    session.refresh(n)
    assert n.status == "cancelled"
    
    # Try cancelling non-existent
    assert reminder_service.cancel_reminder(uuid4()) is False

def test_cleanup_expired_reminders(reminder_service, test_user, session):
    now = datetime.now()
    # Too old (2 hours ago)
    n1 = Notification(user_id=test_user.id, type="r", scheduled_time=now - timedelta(hours=2), status="scheduled")
    # Recently past (30 mins ago) - not cleanup yet
    n2 = Notification(user_id=test_user.id, type="r", scheduled_time=now - timedelta(minutes=30), status="scheduled")
    session.add_all([n1, n2])
    session.commit()
    
    cleaned = reminder_service.cleanup_expired_reminders()
    assert cleaned == 1
    session.refresh(n1)
    assert n1.status == "failed"
