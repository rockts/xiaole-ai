import sys
import os
import face_recognition

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_face_in_uploads():
    uploads_dir = "backend/uploads"
    if not os.path.exists(uploads_dir):
        print(f"Directory not found: {uploads_dir}")
        return

    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(uploads_dir, filename)
            print(f"Checking {filename}...", end="", flush=True)
            try:
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)
                if len(face_locations) > 0:
                    print(f" ✅ Found {len(face_locations)} face(s)!")
                    print(
                        f"Use this command to register: python scripts/register_face.py {image_path} \"User\"")
                    return
                else:
                    print(" ❌ No face")
            except Exception as e:
                print(f" ⚠️ Error: {e}")


if __name__ == "__main__":
    find_face_in_uploads()
