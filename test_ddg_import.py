try:
    from duckduckgo_search import DDGS
    ddgs = DDGS()
    print("DDGS initialized")
    # Test with timelimit
    print("Testing with timelimit='d'...")
    results = list(ddgs.text("latest news", max_results=1, timelimit='d'))
    print(f"Search result (day): {results}")

    print("Testing with timelimit='m'...")
    results = list(ddgs.text("python release", max_results=1, timelimit='m'))
    print(f"Search result (month): {results}")

except Exception as e:
    print(f"Search failed: {e}")
