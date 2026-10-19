"""
Utility functions for ./llm
"""

import datetime


def format_timestamp(timestamp):
    UTC = datetime.timezone.utc
    timestamp = timestamp.astimezone(UTC).isoformat(timespec="milliseconds")
    return timestamp.replace("+00:00", "Z")


def get_timestamp():
    return format_timestamp(datetime.datetime.now())
