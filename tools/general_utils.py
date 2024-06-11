from datetime import datetime
import zoneinfo


def unix_to_datetime(x, tz_str):
    """
    convert unix timestamp to datetime object
    :param x: int = unix timestamp
    :param tz_str: str = timezone string
    :return: datetime object
    """
    timezone = zoneinfo.ZoneInfo(tz_str)
    local_time = datetime.fromtimestamp(x, timezone)
    return local_time


