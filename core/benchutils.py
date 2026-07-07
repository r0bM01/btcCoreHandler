# Copyright [2026-present] [R0BM01@pm.me]                                   #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
# http://www.apache.org/licenses/LICENSE:2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################

import json, hashlib, secrets
import datetime as dt


def checksum(data: bytes) -> str:
    return hashlib.blake2b(data, digest_size = 32).hexdigest()

def from_json(data) -> dict:
    return json.loads(data)

def to_json(data) -> str:
    return json.dumps(data)

def classdate(timestamp: int = False):
    return dt.datetime.fromtimestamp(int(timestamp)) if bool(timestamp) else dt.datetime.now()

def strdate_from_timestamp(timestamp) -> str:
    return dt.datetime.fromtimestamp(int(timestamp)).ctime()

def strtime_delay(sec: int) -> str:
    # only seconds accepted
    delay = dt.timedelta(seconds = sec)
    h = delay.seconds // 3600
    m = (delay.seconds % 3600) // 60 
    s = (delay.seconds % 3600) % 60
    msg = str()
    if bool(delay.days): msg += f"{delay.days} days, "
    if bool(h): msg += f"{h}hours, "
    if bool(m): msg += f"{m}mins and "
    msg += f"{s}seconds"
    return msg

def strtime_delay_diff(start_time) -> str:
    return strtime_delay(timestamp() - int(start_time))

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