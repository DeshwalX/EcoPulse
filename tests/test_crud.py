import pytest
from backend import crud, models
from backend.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Spin up an in-memory database workspace and drop tables upon test completion."""
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_and_get_user(db_session):
    """Test user registration constraints and subsequent account record lookups."""
    user = crud.create_user(
        db_session, username="test_user", password_raw="pwd", role="Client"
    )
    assert user.id is not None
    assert user.username == "test_user"
    assert user.role == "Client"

    fetched_user = crud.get_user_by_username(db_session, "test_user")
    assert fetched_user is not None
    assert fetched_user.id == user.id


def test_prediction_logging_and_history(db_session):
    """Test inference tracking row instantiation and subsequent curation override updates."""
    log = crud.create_prediction_log(
        db=db_session,
        user_id=1,
        image_path="storage/uploads/test.jpg",
        species="Monstera Deliciosa",
        confidence=0.95,
    )
    assert log.id is not None
    assert log.is_verified == 0

    updated_log = crud.update_prediction_verification(
        db=db_session,
        log_id=log.id,
        status=-1,
        correction="Fiddle Leaf Fig",
    )
    assert updated_log.is_verified == -1
    assert updated_log.corrected_species == "Fiddle Leaf Fig"