import os
import json
import cv2
import numpy as np
from typing import Tuple, Optional, Dict, List
from backend.config import settings

MODEL_FILE_PATH = os.path.join(settings.FACES_DIR, "lbph_model.xml")
MAPPING_FILE_PATH = os.path.join(settings.FACES_DIR, "id_mapping.json")

class FaceRecognitionEngine:
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        self.hosteler_map: Dict[int, int] = {}  # label_id -> hosteler_id
        self.is_trained = False
        self.load_model()

    def load_model(self):
        """Loads existing model and hosteler mapping if available."""
        if os.path.exists(MODEL_FILE_PATH) and os.path.exists(MAPPING_FILE_PATH):
            try:
                self.recognizer.read(MODEL_FILE_PATH)
                with open(MAPPING_FILE_PATH, 'r') as f:
                    data = json.load(f)
                    self.hosteler_map = {int(k): int(v) for k, v in data.items()}
                self.is_trained = len(self.hosteler_map) > 0
                print(f"[AI Engine] Loaded face recognition model with {len(self.hosteler_map)} enrolled hostelers.")
            except Exception as e:
                print(f"[AI Engine] Error loading face recognition model: {e}")
                self.is_trained = False
        else:
            self.is_trained = False

    def save_model(self):
        """Saves current trained recognizer model and mapping to disk."""
        try:
            self.recognizer.write(MODEL_FILE_PATH)
            with open(MAPPING_FILE_PATH, 'w') as f:
                json.dump({str(k): v for k, v in self.hosteler_map.items()}, f)
            print("[AI Engine] Saved face recognition model successfully.")
        except Exception as e:
            print(f"[AI Engine] Error saving face recognition model: {e}")

    def train_profiles(self, profiles: List[Tuple[int, np.ndarray]]):
        """
        Trains the recognizer model with a list of (hosteler_id, gray_face_image) tuples.
        """
        if not profiles:
            self.is_trained = False
            return

        faces = []
        labels = []
        self.hosteler_map = {}

        for idx, (hosteler_id, gray_face) in enumerate(profiles):
            if gray_face is None or gray_face.size == 0:
                continue
            
            # Ensure face is resized grayscale (200x200)
            if len(gray_face.shape) == 3:
                gray_face = cv2.cvtColor(gray_face, cv2.COLOR_BGR2GRAY)
            
            if gray_face.shape != (200, 200):
                gray_face = cv2.resize(gray_face, (200, 200))
                
            label = idx + 1
            faces.append(gray_face)
            labels.append(label)
            self.hosteler_map[label] = hosteler_id

        if faces:
            self.recognizer.train(faces, np.array(labels, dtype=np.int32))
            self.is_trained = True
            self.save_model()
        else:
            self.is_trained = False

    def predict(self, face_bgr: np.ndarray, distance_threshold: float = 85.0) -> Tuple[Optional[int], float, bool]:
        """
        Predicts hosteler for a given face BGR image.
        Returns: (hosteler_id, confidence_percentage, is_known)
        LBPH distance: lower means closer match (0 = exact match).
        Distance < 80.0 is typically a valid match.
        """
        if not self.is_trained or face_bgr is None or face_bgr.size == 0:
            return None, 0.0, False

        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY) if len(face_bgr.shape) == 3 else face_bgr
        if gray.shape != (200, 200):
            gray = cv2.resize(gray, (200, 200))

        label, distance = self.recognizer.predict(gray)

        # Convert LBPH distance to intuitive 0-100% confidence scale
        # 0 distance -> 100% match, 100 distance -> 20% match
        confidence = max(0.0, min(100.0, round(100.0 - (distance * 0.7), 2)))

        if distance <= distance_threshold and label in self.hosteler_map:
            hosteler_id = self.hosteler_map[label]
            return hosteler_id, confidence, True
        else:
            return None, confidence, False

# Global AI Recognition Engine Singleton Instance
ai_engine = FaceRecognitionEngine()
