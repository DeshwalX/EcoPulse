import os
from ultralytics import YOLO


class PlantPredictor:
    """Loads weights and coordinates computer vision classification tasks."""

    def __init__(self, weights_path: str = "weights/best.pt"):
        self.weights_path = weights_path
        self.model = YOLO(weights_path) if os.path.exists(weights_path) else None
        if not self.model:
            print(f"Warning: Weights file missing at {weights_path}")

    def predict(self, image_path: str) -> tuple[str, float]:
        """Execute top-1 image classification inference on the target file path."""
        if not self.model:
            raise RuntimeError("Model weights not initialized.")
            
        results = self.model(image_path)
        probs = results[0].probs
        return results[0].names[probs.top1], round(float(probs.top1conf), 4)