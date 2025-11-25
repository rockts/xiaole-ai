from tools.weather_tool import WeatherTool
import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# We need to make sure tools can be imported
sys.path.append(os.path.join(os.getcwd(), 'tools'))


async def test_weather():
    tool = WeatherTool()
    print("\nTesting WeatherTool for '天水'...")

    result = await tool.execute(city='天水', query_type='now')

    print("\nResult:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_weather())
