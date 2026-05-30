from sqlalchemy.orm import Session
from . import auth, models


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Query a user account by their unique username string."""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, username: str, password_raw: str, role: str = "Client") -> models.User:
    """Securely hash raw credentials and register a new User record."""
    db_user = models.User(
        username=username,
        password_hash=auth.get_password_hash(password_raw),
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_prediction_log(db: Session, user_id: int, image_path: str, species: str, confidence: float) -> models.PredictionLog:
    """Log an automated machine learning inference transaction to the history tables."""
    log_entry = models.PredictionLog(
        user_id=user_id,
        image_path=image_path,
        predicted_species=species,
        confidence=confidence
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_user_history(db: Session, user_id: int) -> list[models.PredictionLog]:
    """Retrieve all historical inference entries created by a target user ID."""
    return db.query(models.PredictionLog).filter(models.PredictionLog.user_id == user_id).all()


def get_all_logs(db: Session) -> list[models.PredictionLog]:
    """Fetch all prediction rows across the platform for administrative dashboards."""
    return db.query(models.PredictionLog).all()


def update_prediction_verification(db: Session, log_id: int, status: int, correction: str = None) -> models.PredictionLog | None:
    """Commit an expert curation verification status flag change or text taxonomy override."""
    log_entry = db.query(models.PredictionLog).filter(models.PredictionLog.id == log_id).first()
    if log_entry:
        log_entry.is_verified = status
        if correction:
            log_entry.corrected_species = correction
        db.commit()
        db.refresh(log_entry)
    return log_entry