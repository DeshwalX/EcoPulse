import os
import shutil
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from . import auth, crud, models
from .database import Base, engine, get_db
from .predictor import PlantPredictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle automated database structural migrations and seed accounts on startup."""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    if not crud.get_user_by_username(db, "client_demo"):
        crud.create_user(db, "client_demo", "password123", "Client")
    if not crud.get_user_by_username(db, "botanist_demo"):
        crud.create_user(db, "botanist_demo", "expert123", "Botanist")
    if not crud.get_user_by_username(db, "admin_demo"):
        crud.create_user(db, "admin_demo", "admin123", "Admin")
    yield


app = FastAPI(title="EcoPulse Plant Curation API Engine", lifespan=lifespan)
predictor = PlantPredictor()


@app.post("/api/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Authenticate user credentials and return application role profile access permissions."""
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"user_id": user.id, "username": user.username, "role": user.role}


@app.post("/api/predict")
async def run_inference(user_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Process uploaded binary image files and trigger YOLO taxonomy classification."""
    storage_dir = "storage/uploads"
    os.makedirs(storage_dir, exist_ok=True)

    file_path = os.path.join(storage_dir, f"{user_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    species, confidence = predictor.predict(file_path)
    log = crud.create_prediction_log(db, user_id, file_path, species, confidence)

    return {
        "log_id": log.id,
        "predicted_species": species,
        "confidence": confidence,
        "timestamp": log.timestamp,
    }


@app.get("/api/history/{user_id}")
def read_history(user_id: int, db: Session = Depends(get_db)):
    """Fetch individual historical inference prediction transactions for a customer."""
    return crud.get_user_history(db, user_id)


@app.get("/api/logs/all")
def read_all_logs(db: Session = Depends(get_db)):
    """Provide global auditing tracking matrix tables for privileged management roles."""
    return crud.get_all_logs(db)


@app.post("/api/curate")
def update_log(log_id: int = Form(...), status: int = Form(...), correction: str = Form(None), db: Session = Depends(get_db)):
    """Update database log entry validation flags and commit human-in-the-loop expert corrections."""
    updated_log = crud.update_prediction_verification(db, log_id, status, correction)
    if not updated_log:
        raise HTTPException(status_code=404, detail="Target log tracking trace asset index missing")
    return {"status": "Success", "message": "Log updated successfully."}