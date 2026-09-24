"""
Utility functions for ./llm
"""

import datetime

def get_timestamp():
    UTC = datetime.timezone.utc
    timestamp = datetime.datetime.now(UTC).isoformat(timespec="milliseconds")
    return timestamp.replace("+00:00", "Z")
