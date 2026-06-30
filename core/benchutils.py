

import json, hashlib, secrets
import datetime as dt


def checksum(data: bytes) -> str:
    return hashlib.blake2b(data, digest_size = 32).hexdigest()

def from_json(data) -> dict:
    return json.loads(data)

def to_json(data) -> str:
    return json.dumps(data)

def timestamp(delay: int = 0) -> int:
    return int(dt.datetime.now().timestamp()) + delay

def timestamp_from_date(year = False, month = False, day = False) -> int:
    year = year or dt.datetime.now().year
    month = month or dt.datetime.now().month
    day = day or dt.datetime.now().day
    return int(dt.datetime(year, month, day).timestamp())

def timestamp_from_time(hour = 0, minute = 0, second = 0) -> int:
    year = dt.datetime.now().year
    month = dt.datetime.now().month
    day = dt.datetime.now().day
    return int(dt.datetime(year, month, day, hour, minute, second).timestamp())