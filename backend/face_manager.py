import face_recognition
import numpy as np
from sqlalchemy.orm import Session
from db_setup import SessionLocal, FaceEncoding
import os
import logging

logger = logging.getLogger(__name__)


class FaceManager:
    def __init__(self):
        # We should create a new session per request or manage it better.
        # But for now, let's keep it simple but safe.
        pass

    def get_db(self):
        return SessionLocal()

    def register_face(
        self, image_path: str, name: str, user_id: str = "default_user"
    ):
        """
        Register a face.
        Returns: dict with success, result/error
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}

        db = self.get_db()
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)

            # Detect faces
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 0:
                return {"success": False, "error": "No face detected in the image"}
            if len(face_locations) > 1:
                return {"success": False, "error": "Multiple faces detected. Please upload an image with a single face."}

            # Extract encoding
            face_encodings = face_recognition.face_encodings(
                image, face_locations)
            if len(face_encodings) == 0:
                return {"success": False, "error": "Could not extract face encoding"}

            # Convert numpy array to list for DB storage
            encoding = face_encodings[0].tolist()

            # Save to DB
            new_face = FaceEncoding(
                user_id=user_id,
                name=name,
                encoding=encoding,
                image_path=image_path
            )

            db.add(new_face)
            db.commit()

            return {"success": True, "result": f"Face registered successfully for {name}"}

        except Exception as e:
            db.rollback()
            logger.error(f"Error registering face: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def get_known_faces(self, user_id: str = "default_user"):
        """
        Get known faces.
        Returns: (encodings, names)
        """
        db = self.get_db()
        try:
            faces = db.query(FaceEncoding).filter(
                FaceEncoding.user_id == user_id
            ).all()
            encodings = []
            names = []
            for face in faces:
                if face.encoding:
                    encodings.append(np.array(face.encoding))
                    names.append(face.name)
            return encodings, names
        finally:
            db.close()

    def recognize_faces(self, image_path: str, user_id: str = "default_user"):
        """
        Recognize faces in an image.
        Returns: dict with success, identified_people, face_count
        """
        if not os.path.exists(image_path):
            return {"success": False, "error": f"Image file not found: {image_path}"}

        known_encodings, known_names = self.get_known_faces(user_id)

        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                return {
                    "success": True,
                    "identified_people": [],
                    "face_count": 0
                }

            face_encodings = face_recognition.face_encodings(
                image, face_locations)

            found_names = []

            if not known_encodings:
                # No known faces, all are unknown
                found_names = ["未知人物"] * len(face_locations)
            else:
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_encodings, face_encoding, tolerance=0.6
                    )
                    name = "未知人物"

                    face_distances = face_recognition.face_distance(
                        known_encodings, face_encoding
                    )
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_names[best_match_index]

                    found_names.append(name)

            return {
                "success": True,
                "identified_people": found_names,
                "face_count": len(face_locations)
            }

        except Exception as e:
            logger.error(f"Error recognizing faces: {e}")
            return {"success": False, "error": str(e)}
