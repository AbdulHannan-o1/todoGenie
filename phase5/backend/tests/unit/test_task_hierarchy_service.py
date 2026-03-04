import pytest
from sqlmodel import Session, SQLModel, create_engine
from uuid import uuid4
from src.services.task_hierarchy_service import TaskHierarchyService
from src.models import User, Task, TaskCreate
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

@pytest.fixture(name="hierarchy_service")
def hierarchy_service_fixture(session):
    return TaskHierarchyService(session)

@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        id=uuid4(),
        email="hierarchy@example.com",
        username="huser",
        hashed_password="password",
        status="Active"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def create_task(session, user_id, title, parent_id=None):
    task = Task(id=uuid4(), title=title, user_id=user_id, parent_task_id=parent_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def test_get_task_with_hierarchy(hierarchy_service, test_user, session):
    parent = create_task(session, test_user.id, "Parent")
    child = create_task(session, test_user.id, "Child", parent.id)
    
    result = hierarchy_service.get_task_with_hierarchy(child.id, test_user.id)
    assert result["task"].id == child.id
    assert result["parent"].id == parent.id
    assert len(result["children"]) == 0
    
    result = hierarchy_service.get_task_with_hierarchy(parent.id, test_user.id)
    assert result["parent"] is None
    assert len(result["children"]) == 1
    assert result["children"][0].id == child.id

def test_get_full_hierarchy_recursive(hierarchy_service, test_user, session):
    root = create_task(session, test_user.id, "Root")
    c1 = create_task(session, test_user.id, "C1", root.id)
    c2 = create_task(session, test_user.id, "C2", root.id)
    gc1 = create_task(session, test_user.id, "GC1", c1.id)
    
    hierarchy = hierarchy_service.get_full_hierarchy(root.id, test_user.id)
    assert hierarchy["task"].id == root.id
    assert len(hierarchy["children"]) == 2
    
    # Verify GC1 is under C1
    c1_node = next(c for c in hierarchy["children"] if c["task"].id == c1.id)
    assert len(c1_node["children"]) == 1
    assert c1_node["children"][0]["task"].id == gc1.id

def test_move_task(hierarchy_service, test_user, session):
    t1 = create_task(session, test_user.id, "T1")
    t2 = create_task(session, test_user.id, "T2")
    
    # Move T2 under T1
    assert hierarchy_service.move_task_under_parent(t2.id, t1.id, test_user.id) is True
    session.refresh(t2)
    assert t2.parent_task_id == t1.id
    
    # Move to root
    assert hierarchy_service.move_task_under_parent(t2.id, None, test_user.id) is True
    session.refresh(t2)
    assert t2.parent_task_id is None

def test_get_root_tasks(hierarchy_service, test_user, session):
    root1 = create_task(session, test_user.id, "R1")
    root2 = create_task(session, test_user.id, "R2")
    create_task(session, test_user.id, "C", root1.id)
    
    roots = hierarchy_service.get_root_tasks(test_user.id)
    assert len(roots) == 2
    assert all(r.parent_task_id is None for r in roots)

def test_count_descendants(hierarchy_service, test_user, session):
    root = create_task(session, test_user.id, "Root")
    c1 = create_task(session, test_user.id, "C1", root.id)
    create_task(session, test_user.id, "GC1", c1.id)
    create_task(session, test_user.id, "C2", root.id)
    
    assert hierarchy_service.count_descendants(root.id, test_user.id) == 3
    assert hierarchy_service.count_descendants(c1.id, test_user.id) == 1

def test_create_child_task(hierarchy_service, test_user, session):
    parent = create_task(session, test_user.id, "Parent")
    request = TaskCreate(title="New Child", priority="high")
    
    child = hierarchy_service.create_child_task(parent.id, request, test_user.id)
    assert child.parent_task_id == parent.id
    assert child.title == "New Child"
    assert child.priority == "high"

def test_get_task_ancestors(hierarchy_service, test_user, session):
    root = create_task(session, test_user.id, "Root")
    c1 = create_task(session, test_user.id, "C1", root.id)
    gc1 = create_task(session, test_user.id, "GC1", c1.id)
    
    ancestors = hierarchy_service.get_task_ancestors(gc1.id, test_user.id)
    # Reversed in service returns [Root, C1]
    assert len(ancestors) == 2
    assert ancestors[0].id == root.id
    assert ancestors[1].id == c1.id
