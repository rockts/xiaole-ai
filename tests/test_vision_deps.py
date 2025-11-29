
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    print("Testing imports...")
    try:
        import cv2
        print(f"✅ OpenCV imported successfully. Version: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import cv2: {e}")
        return False

    try:
        import face_recognition
        print(
            f"✅ face_recognition imported successfully. Version: {face_recognition.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import face_recognition: {e}")
        return False

    return True


if __name__ == "__main__":
    if test_imports():
        sys.exit(0)
    else:
        sys.exit(1)
