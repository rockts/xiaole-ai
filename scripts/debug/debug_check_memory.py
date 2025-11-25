from memory import MemoryManager
import sys


def check_memory():
    try:
        memory = MemoryManager()
        # Check facts
        facts = memory.recall(tag="facts", limit=50)
        print("=== Facts Memory ===")
        found_location = False
        for fact in facts:
            print(f"- {fact}")
            if "天水" in fact or "城市" in fact or "住" in fact:
                found_location = True

        if found_location:
            print("\n✅ Found location related info in memory.")
        else:
            print("\n❌ No location related info found in 'facts' tag.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_memory()
