import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from .database import Base


class User(Base):
    """System accounts mapping credentials and authorization roles."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="Client")


class PredictionLog(Base):
    """Historical records of model predictions and expert curation overrides."""

    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String, nullable=False)
    predicted_species = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    is_verified = Column(Integer, default=0)  # 0: Pending, 1: Approved, -1: Overridden
    corrected_species = Column(String, nullable=True)