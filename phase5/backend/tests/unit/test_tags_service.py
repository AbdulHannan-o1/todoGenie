import pytest
from sqlmodel import Session, SQLModel, create_engine
from uuid import uuid4
from src.services.tags_service import TagsService
from src.models import User, Tag, Task, TaskTag
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

@pytest.fixture(name="tags_service")
def tags_service_fixture(session):
    return TagsService(session)

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        id=uuid4(),
        email="tagtest@example.com",
        username="taguser",
        hashed_password="password",
        status="Active"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_create_tag(tags_service, test_user):
    tag = tags_service.create_tag(test_user.id, "Work", "blue")
    assert tag.name == "Work"
    assert tag.color == "blue"
    assert tag.user_id == test_user.id

def test_get_user_tags(tags_service, test_user):
    tags_service.create_tag(test_user.id, "Work")
    tags_service.create_tag(test_user.id, "Personal")
    
    tags = tags_service.get_user_tags(test_user.id)
    assert len(tags) == 2
    assert any(t.name == "Work" for t in tags)
    assert any(t.name == "Personal" for t in tags)

def test_get_tag_by_id(tags_service, test_user):
    tag = tags_service.create_tag(test_user.id, "Unique")
    
    found = tags_service.get_tag_by_id(tag.id, test_user.id)
    assert found is not None
    assert found.name == "Unique"
    
    # Try different user
    not_found = tags_service.get_tag_by_id(tag.id, uuid4())
    assert not_found is None

def test_update_tag(tags_service, test_user):
    tag = tags_service.create_tag(test_user.id, "Old")
    
    updated = tags_service.update_tag(tag.id, test_user.id, name="New", color="red")
    assert updated.name == "New"
    assert updated.color == "red"
    
    # Update only color
    updated = tags_service.update_tag(tag.id, test_user.id, color="green")
    assert updated.name == "New"
    assert updated.color == "green"

def test_delete_tag(tags_service, test_user):
    tag = tags_service.create_tag(test_user.id, "Disposable")
    
    success = tags_service.delete_tag(tag.id, test_user.id)
    assert success is True
    assert tags_service.get_tag_by_id(tag.id, test_user.id) is None
    
    # Try deleting non-existent
    fail = tags_service.delete_tag(uuid4(), test_user.id)
    assert fail is False

def test_task_tag_assignment(tags_service, test_user, session):
    task = Task(title="Tagged Task", user_id=test_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    
    tag = tags_service.create_tag(test_user.id, "TaskTag")
    
    # Assign
    assert tags_service.assign_tag_to_task(task.id, tag.id) is True
    # Re-assign (should return True but not duplicate)
    assert tags_service.assign_tag_to_task(task.id, tag.id) is True
    
    tags = tags_service.get_tags_for_task(task.id)
    assert len(tags) == 1
    assert tags[0].id == tag.id
    
    tasks = tags_service.get_tasks_for_tag(tag.id, test_user.id)
    assert len(tasks) == 1
    assert tasks[0].id == task.id

def test_remove_tag_from_task(tags_service, test_user, session):
    task = Task(title="Untagged Task", user_id=test_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    
    tag = tags_service.create_tag(test_user.id, "RemoveMe")
    tags_service.assign_tag_to_task(task.id, tag.id)
    
    assert tags_service.remove_tag_from_task(task.id, tag.id) is True
    assert len(tags_service.get_tags_for_task(task.id)) == 0
    
    # Try removing non-existent assignment
    assert tags_service.remove_tag_from_task(task.id, tag.id) is False
