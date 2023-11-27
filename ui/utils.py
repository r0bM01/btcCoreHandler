
def convertBytesSizes(numBytes):
    size = {}
    size['KiB'] = 1024
    size['MiB'] = size['KiB'] * 1024
    size['GiB'] = size['MiB'] * 1024
    size['TiB'] = size['GiB'] * 1024

    for key, value in size.items():
        if int(numBytes) > value:
            resValue = int(numBytes) / value
            resSize = str(key) 
    return str(f"{resValue:.2f} {resSize}")

def convertElapsedTime(numSeconds):
    numSeconds = int(numSeconds)
    result = []
    if numSeconds // 604800:
        result.append(str(f"{numSeconds // 604800} Weeks"))
        numSeconds %= 604800
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
        return str(f"{int(num * 100)}%")
    else:
        return num

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