import sys
import os

# Simulate the environment in backend/routers/vision.py
# Original code:
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# This adds 'backend' to sys.path

current_dir = os.getcwd()
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

print(f"sys.path: {sys.path}")

try:
    import tools
    print(f"Imported tools: {tools}")
    print(f"tools file: {getattr(tools, '__file__', 'None')}")
    print(f"tools path: {getattr(tools, '__path__', 'None')}")
except ImportError as e:
    print(f"Failed to import tools: {e}")

try:
    from tools.vision_tool import VisionTool
    print("Successfully imported VisionTool")
except ImportError as e:
    print(f"Failed to import VisionTool: {e}")
except Exception as e:
    print(f"Other error importing VisionTool: {e}")
