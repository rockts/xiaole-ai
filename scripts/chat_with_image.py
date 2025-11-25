from backend.agent import XiaoLeAgent
import sys
import os
import time

# Add project root to python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "backend"))


def test_chat_with_image():
    print("🤖 Initializing Agent...")
    agent = XiaoLeAgent()

    image_path = "files/obama.jpg"
    prompt = "这张图里是谁？"

    print(f"\n👤 User: {prompt}")
    print(f"🖼️ Image: {image_path}")

    try:
        response = agent.chat(prompt, image_path=image_path)
        print(f"\n🤖 Agent: {response['reply']}")

        if "Obama" in response['reply'] or "奥巴马" in response['reply']:
            print("\n✅ SUCCESS: Agent identified the person!")
        else:
            print("\n⚠️ WARNING: Agent might not have identified the person correctly.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    test_chat_with_image()
