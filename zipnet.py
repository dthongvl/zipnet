from struct import unpack
import requests

url = "http://zlib.net/zlib128-dll.zip"

def getFileSize(url):
    req = requests.head(url)
    return int(req.headers['Content-Length'])

def getDataWithRange(start, end):
    rangeToDownload = 'bytes=%s-%s' % (start, end)
    headers = {'Range' : rangeToDownload}
    req = requests.get(url, headers = headers)
    return req.content

def getEndOfCentralData(fileSize):
    return getDataWithRange(fileSize - 22, fileSize)

def getCentralDirectoryData(offsetOfCd, centralSize):
    return getDataWithRange(offsetOfCd, offsetOfCd + centralSize)

def getCentralDirectoryInfo(data):
    pos = 0

    signature = data[pos: pos + 4].encode('hex')
    pos += 10

    totalentries = unpack('<H', data[pos: pos + 2])[0]

    pos += 2
    centralsize = unpack('<L', data[pos: pos + 4])[0]

    pos += 4
    offsetofcd = unpack('<L', data[pos: pos + 4])[0]

    return signature, totalentries, centralsize, offsetofcd

def listFileAtPos(data, pos):
    signature = data[pos: pos + 4].encode('hex')

    pos += 12
    time = unpack('<H', data[pos: pos + 2])[0]
    time = "{:16b}".format(time)
    if time[0:5] != "     ":
        hours = str(int(time[0:5], 2))
    else:
        hours = ""
    minutes = str(int(time[5:11], 2))
    second = str(int(time[11:], 2)*2)
    modifiedTime = hours + ':' + minutes + ':' + second

    pos += 2
    date = unpack('<H', data[pos: pos + 2])[0]
    date = "{:16b}".format(date)
    if date[0:5] != "     ":
        year = str(int(date[0:7], 2) + 1980)
    else:
        year = ""
    month = str(int(date[7:11], 2))
    day = str(int(date[11:], 2))
    modifiedDate = day + '/' + month + '/' + year

    pos += 6

    compressedSize = unpack('<L', data[pos: pos + 4])[0]

    pos += 4
    uncompressedSize = unpack('<L', data[pos: pos + 4])[0]

    pos += 4
    lenFileName = unpack('<H', data[pos: pos + 2])[0]

    pos += 2
    lenExtraField = unpack('<H', data[pos: pos + 2])[0]

    pos += 2
    lenComment = unpack('<H', data[pos: pos + 2])[0]

    pos += 14
    fileName = data[pos: pos + lenFileName]
    
    print "File name: " + fileName
    print "Compressed Size: " + str(compressedSize) + " bytes"
    print "Uncompressed Size: " + str(uncompressedSize) + " bytes"
    print "Modified at: " + modifiedTime + " " + modifiedDate

    print "--------------------------------------"

    pos += lenFileName + lenExtraField + lenComment

    return pos

fileSize = getFileSize(url)
endOfCentralData = getEndOfCentralData(fileSize)
signature, totalEntries, centralSize, offsetOfCd = getCentralDirectoryInfo(endOfCentralData)
centralDirectoryData = getCentralDirectoryData(offsetOfCd, centralSize)

pos = 0

for x in range(totalEntries):
    pos = listFileAtPos(centralDirectoryData, pos)
    
print "TOTAL ENTRIES: " + str(totalEntries)

