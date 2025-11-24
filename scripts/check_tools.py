from agent import XiaoLeAgent
from tool_manager import get_tool_registry
import sys
import os

# Add project root and backend to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))


# Initialize agent to trigger tool registration
agent = XiaoLeAgent()

registry = get_tool_registry()
tools = registry.get_tool_names()

print(f"Registered tools: {tools}")

if "vision_analysis" in tools:
    print("✅ VisionTool is registered successfully!")
else:
    print("❌ VisionTool is NOT registered.")
