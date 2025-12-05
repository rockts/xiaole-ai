import sys
import numpy as np

print(f"Python version: {sys.version}")

try:
    import cv2
    print(f"✅ OpenCV imported successfully. Version: {cv2.__version__}")
except ImportError as e:
    print(f"❌ Failed to import cv2: {e}")

try:
    import face_recognition
    print(
        f"✅ face_recognition imported successfully. Version: {face_recognition.__version__}")
except ImportError as e:
    print(f"❌ Failed to import face_recognition: {e}")


def test_detection():
    print("\n🧪 Testing basic face detection functionality...")
    try:
        # Create a black image (100x100)
        image = np.zeros((100, 100, 3), dtype="uint8")

        # Try to find face locations (should be empty, but tests the function)
        face_locations = face_recognition.face_locations(image)
        print(
            f"✅ face_recognition.face_locations() called successfully. Found {len(face_locations)} faces (expected 0).")

        print("\n🎉 Environment check passed! You are ready for Phase 1.")
    except Exception as e:
        print(f"\n❌ Runtime error during detection test: {e}")


if __name__ == "__main__":
    test_detection()
