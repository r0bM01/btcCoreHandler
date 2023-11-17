
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