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


import json, base64, ssl
from urllib import request
from core import env



def get_external_ips() -> list:
    endpoints = ["https://api.ipify.org", "https://api64.ipify.org"]
    ips = list()
    for ep in endpoints:
        req = request.urlopen(url = ep, context = ssl.create_default_context())
        if req.status == 200:
            ip = ipaddress.ip_address(req.read().decode())
            if ip not in ips:
                ips.append(ip)
    return ips

def get_geolocation(ip_addr) -> dict:
    req = request.Request(url = "https://json.geoiplookup.io/" + str(ip_addr), headers = {'User-Agent': 'Mozilla/5.0'})
    res = request.urlopen(url = req, context = ssl.create_default_context()).read().decode()
    geo = json.loads(res)
    geo['checksum'] = Utils.make_checksum(str("".join([str(geo[v]) for v in geo if v != 'ip'])).encode('utf-8'))
    return geo

def get_bitcoin_daemon(command) -> json:
    url = "http://" + str(env.BTCDAEMON_HOST) + ":" + str(env.BTCDAEMON_PORT)
    usr = env.BTCDAEMON_USER.encode('utf-8')
    psw = env.BTCDAEMON_PASS.encode('utf-8')
    auth = base64.b64encode(usr + b':' + psw)
    auth = auth.decode()
    header = {'content-type': 'application/json', 'Authorization': 'Basic ' + auth}
    req = request.Request(url = url, data = json.dumps(command).encode('utf-8'), headers = header)
    res = request.urlopen(req).read().decode()
    return json.loads(res)

def send_nextcloud_msg(message) -> bool:
    url = "https://cloud.bareminds.eu/ocs/v2.php/apps/spreed/api/v1/chat/" + env.NEXTCLOUD_CHAT
    usr = env.NEXTCLOUD_USER.encode('utf-8')
    psw = env.NEXTCLOUD_PASS.encode('utf-8')
    auth = base64.b64encode(usr + b':' + psw)
    auth = auth.decode()
    header = {'User-Agent': 'Mozilla/5.0', 'content-type': 'application/json', 'OCS-APIRequest': 'true', 'Authorization': 'Basic ' + auth}
    data = json.dumps({'token': env.NEXTCLOUD_CHAT, 'message': message, 'silent': False})
    req = request.Request(url = url, data = data.encode('utf-8'), headers = header)
    res = request.urlopen(req)
    return True if res.status == 201 or res.status == 200 else False