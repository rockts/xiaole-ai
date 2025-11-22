from reminder_manager import get_reminder_manager
from tools.reminder_tool import ReminderTool
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root and backend to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, "backend"))


async def debug_reminder_tool_list():
    tool = ReminderTool()
    user_id = "default_user"

    print(f"--- Debugging ReminderTool List for {user_id} ---")

    # Call the tool exactly as the agent would
    result = await tool.execute(
        operation="list",
        user_id=user_id
    )

    print(f"Result Success: {result['success']}")
    print(f"Result Data:\n{result['data']}")

if __name__ == "__main__":
    asyncio.run(debug_reminder_tool_list())
