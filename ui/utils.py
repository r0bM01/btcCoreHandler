# Copyright [2023] [R0BM01@pm.me]                                           #
#                                                                           #
# Licensed under the Apache License, Version 2.0 (the "License");           #
# you may not use this file except in compliance with the License.          #
# You may obtain a copy of the License at                                   #
#                                                                           #
# http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                           #
# Unless required by applicable law or agreed to in writing, software       #
# distributed under the License is distributed on an "AS IS" BASIS,         #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
# See the License for the specific language governing permissions and       #
# limitations under the License.                                            #
#############################################################################

import time
from collections import Counter


def uptimeSince(uptime):
    timeNow = time.time()
    upSince = str(time.ctime(timeNow - int(uptime)))
    return upSince

def printSystem(systemInfo):
    printable = str()
    for key, value in systemInfo.items():
        printable += str(value) + " "
    return printable

def convertBytesSizes(numBytes):
    
    size = {}
    size['KiB'] = 1024
    size['MiB'] = size['KiB'] * 1024
    size['GiB'] = size['MiB'] * 1024
    size['TiB'] = size['GiB'] * 1024

    if int(numBytes) < size['KiB']: return str(f"{numBytes} Bytes")
    for key, value in size.items():
        if int(numBytes) > value:
            resValue = int(numBytes) / value
            resSize = str(key)
    return str(f"{resValue:.2f} {resSize}")

def convertBigSizes(bigNum):
    size = {}
    size['M'] = 1000000
    size['G'] = size['M'] * 1000
    size['T'] = size['G'] * 1000
    size['P'] = size['T'] * 1000
    size['E'] = size['P'] * 1000
    size['Z'] = size['E'] * 1000

    for key, value in size.items():
        if int(bigNum) > value:
            resValue = int(bigNum) / value
            resSize = str(key)
    return str(f"{resValue:.2f} {resSize}")


def convertElapsedTime(numSeconds):
    numSeconds = int(numSeconds)
    result = []
    # if numSeconds // 604800:
    #     result.append(str(f"{numSeconds // 604800} Weeks"))
    #     numSeconds %= 604800
    if numSeconds // 86400:
        result.append(str(f"{numSeconds // 86400} Days"))
        numSeconds %= 86400
    if numSeconds // 3600:
        result.append(str(f"{numSeconds// 3600} Hours"))
        numSeconds %= 3600
    if numSeconds // 60:
        result.append(str(f"{numSeconds // 60} Mins"))
        numSeconds %= 60
    if numSeconds:
        result.append(str(f"{numSeconds} Secs"))
    return " ".join(result)

def convertPercentage(num):
    num = float(num)
    if num < 100:
        return str(f"{(num * 100):.2f} %")
    else:
        return num

def convertSatsDigits(num):
    num = float(num)
    return str(f"{num:.8f}")

def convertLongCountry(country):
    if str(country) == "United Kingdom of Great Britain and Northern Ireland":
        country = "United Kingdom"
    else:
        country = str(country)
    return country
    

def countriesStatsList(connectedInfo):
    countries = {}
    for peer in connectedInfo:
        if peer['country_name'] in countries:
            countries[peer['country_name']] += 1  
        else:
            countries[peer['country_name']] = 1
    return countries

def countriesStatsCount(connectedInfo):
    countries = countriesStatsList(connectedInfo)
    return len(countries)


def convertToPrintable(data):
    def prtList(dataL):
        rsl = str()
        for i in dataL:
            rsl += str(f"{i} ")
        return rsl

    def prtDict(dataD):
        rsl = str()
        for key, value in dataD.items():
            rsl += str(f"{key}: {value} ")
        return rsl

    def prtValue(dataValue):
        if type(dataValue) is list: rsl = prtList(dataValue)
        elif type(dataValue) is dict: rsl = prtDict(dataValue)
        else: rsl = dataValue
        return rsl

    printableResult = str()
    
    if type(data) is list:
        for i in data:
            printableResult += prtValue(i) + str("\n")
    elif type(data) is dict:
        for key, value in data.items():
            printableResult += str(f"{key}: ")
            printableResult += str(prtValue(value)) + str("\n")
    else:
        printableResult = str(data) + str("\n")
    return printableResult
