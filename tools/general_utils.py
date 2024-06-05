from datetime import datetime
import zoneinfo


def unix_to_datetime(x, tz_str):
    timezone = zoneinfo.ZoneInfo(tz_str)
    local_time = datetime.fromtimestamp(x, timezone)
    return local_time
