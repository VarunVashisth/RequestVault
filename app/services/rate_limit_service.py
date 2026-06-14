import time

WINDOW_SECONDS = 60
MAX_REQUESTS = 100

usage = {}


def check_rate_limit(api_key):

    now = time.time()

    if api_key not in usage:
        usage[api_key] = []

    timestamps = usage[api_key]

    cutoff = now - WINDOW_SECONDS

    while timestamps and timestamps[0] < cutoff:
        timestamps.pop(0)

    if len(timestamps) >= MAX_REQUESTS:
        return False

    timestamps.append(now)

    return True