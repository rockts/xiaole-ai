from db_setup import SessionLocal, FaceEncoding
import sys
import os

# Add project root and backend to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))


def list_faces():
    db = SessionLocal()
    try:
        faces = db.query(FaceEncoding).all()
        print(f"Found {len(faces)} faces in database:")
        for face in faces:
            print(
                f"- ID: {face.id}, Name: {face.name}, Created: {face.created_at}")
    finally:
        db.close()


if __name__ == "__main__":
    list_faces()
