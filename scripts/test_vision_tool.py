from tools.vision_tool import VisionTool
import sys
import os
import asyncio

# Add project root to python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))


async def test_vision():
    tool = VisionTool()
    image_path = "files/obama.jpg"

    print(f"Testing VisionTool with {image_path}...")
    result = await tool.execute(image_path=image_path)

    print("Result:")
    print(result)

    if result['success'] and "Obama" in result['result']['people']:
        print("✅ Test PASSED: Identified Obama!")
    else:
        print("❌ Test FAILED: Did not identify Obama.")

if __name__ == "__main__":
    asyncio.run(test_vision())
