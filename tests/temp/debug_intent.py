from backend.agent import XiaoLeAgent
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))


def test_intent():
    agent = XiaoLeAgent()
    prompt = "今天天气怎么样"

    print(f"\nTesting intent analysis for prompt: '{prompt}'")

    # Call _analyze_intent directly
    # Note: _analyze_intent is "private" but we can call it for debugging
    analysis = agent._analyze_intent(prompt)

    print("\nAnalysis Result:")
    print(analysis)


if __name__ == "__main__":
    test_intent()
