from backend.db_setup import SessionLocal, FaceEncoding
import sys
import os
import argparse
import face_recognition
import cv2
from sqlalchemy.orm import Session

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def register_face(image_path: str, name: str, user_id: str = "default_user"):
    print(f"📸 Processing image: {image_path}")

    if not os.path.exists(image_path):
        print(f"❌ Error: File not found: {image_path}")
        return

    try:
        # Load image
        image = face_recognition.load_image_file(image_path)

        # Detect faces
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            print("❌ No face detected in the image.")
            return

        if len(face_locations) > 1:
            print(
                f"⚠️ Warning: Found {len(face_locations)} faces. Using the first one.")

        # Get face encodings
        # We assume the first face is the target
        face_encoding = face_recognition.face_encodings(
            image, face_locations)[0]

        # Convert numpy array to list for database storage
        encoding_list = face_encoding.tolist()

        # Save to DB
        db: Session = SessionLocal()
        try:
            new_face = FaceEncoding(
                user_id=user_id,
                name=name,
                encoding=encoding_list,
                image_path=image_path
            )
            db.add(new_face)
            db.commit()
            db.refresh(new_face)
            print(
                f"✅ Successfully registered face for '{name}' (ID: {new_face.id})")
        except Exception as e:
            print(f"❌ Database error: {e}")
            db.rollback()
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error processing image: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Register a face for Xiaole AI")
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument("name", help="Name of the person")
    parser.add_argument("--user_id", default="default_user",
                        help="User ID (default: default_user)")

    args = parser.parse_args()

    register_face(args.image_path, args.name, args.user_id)
