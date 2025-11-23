import re
from datetime import datetime, timedelta


def parse_time(time_desc):
    now = datetime.now()
    time_desc = time_desc.strip()
    print(f"Parsing: '{time_desc}'")

    # 1. 处理"X小时后"
    match = re.search(r'(\d+)\s*[个]?\s*小时后', time_desc)
    if match:
        hours = int(match.group(1))
        print(f"Matched hours: {hours}")
        return now + timedelta(hours=hours)

    print("No match for hours")
    return None


parse_time("1小时后")
parse_time("1个小时后")
parse_time(" 1 小时后 ")
