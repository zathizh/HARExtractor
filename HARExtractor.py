#! /usr/bin/python

import argparse
import json
import base64 
import os

_FMT = "{:06d}"


# get original file name
def getOrgFileName(url):
    return url.split("/").pop()


# generate file name
def getFileName(name, ext):
    return name + "." + ext

# generate the save name
def genSaveName(name, ext, counter, keep):
    global _FMT
    fmt = _FMT.format(counter)
    prefix = fmt + name if keep else fmt
    return getFileName(prefix, ext)


# create file path
def createFilePath(path):
    if not os.path.exists(path):
        os.makedirs(path)


# generate file path
def setFilePath(path):
    path = os.path.join(path, '') 
    createFilePath(path)
    return path


# return file extension
def getFileExtension(mimeType):
    return mimeType.split("/")[1]


#check if HAR file exists
def checkHARFileExists(fileName):
    if not os.path.isfile(fileName):
        print("[-] ERROR : Could Not Find the " + fileName)
        exit(1)


# prints the verbose output
def printFileList(fileSaveName, encoding, _prefix, allFiles, b64, nb64, fTypes, extension):
    if fTypes and extension in fTypes:
        print(_prefix, end="  ")
        print(fileSaveName, end="  ")
    elif encoding == "base64" and (b64 or allFiles) :
        print(_prefix, end="  ")
        print(fileSaveName, end="  ")
        print("--  ", end="")
        print(encoding, end="")
    elif not encoding and (nb64 or allFiles) :
        print(_prefix, end="  ")
        print(fileSaveName, end="  ")
    else :
        return True
    print()
    return False


#handle command line arguments
def argsHandler():
    parser = argparse.ArgumentParser(prog="HARExtractor")
    parser.add_argument("-f", "--file", dest="file", action="store", type=str, required=True, help="file name")
    parser.add_argument("-o", "--out", dest="out", action="store", type=str, default="out", required=False, help="output directory")
    parser.add_argument("-s", "--select", dest="select", action="store", type=str, required=False, help="select by file name")
    parser.add_argument("-c", "--prefix", dest="prefix", action="store", type=int, default=1, required=False, help="Prefix")
    parser.add_argument("-k", "--keep", dest="keep", action="store_true", required=False, help="keep original file name")
    parser.add_argument("-l", "--list", dest="list", action="store_true", required=False, help="list files")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--all", dest="all", action="store_true", default=False, required=False, help="extract all")
    group.add_argument("-b", "--b64", dest="b64", action="store_true", default=False, required=False, help="base64 files only")
    group.add_argument("-n", "--nb64", dest="nb64", action="store_true", default=False, required=False, help="non-base64 files only")
    group.add_argument("-t", "--type", dest="type", action="store", default=False, required=False, nargs='+', help="file type")

    parser.add_argument("-v", "--version", action="version", version='%(prog)s 2.0')

    args = parser.parse_args()
    print (args)
    #exit(1)
    return args


# the main function 
def main():
    args = argsHandler()

    fileName, outPath, selection, listFiles, keep, _prefix = args.file, args.out, args.select, args.list, args.keep, args.prefix

    allFiles, b64, nb64, fTypes = args.all, args.b64, args.nb64, args.type

    checkHARFileExists(fileName)

    with open(fileName, "rb") as harFile:
        har = json.load(harFile)
        entries = har["log"]["entries"]
        for entry in entries:
            if "request" in entry:
                request = entry["request"]
                if "url" in request:
                    url = request["url"]
            if "response" in entry:
                response = entry["response"]
                if "content" in response:
                    content = response["content"]

                    size = mimeType = text = encoding = ""

                    if "size" in content:
                        size = content["size"]
                    if "mimeType" in content:
                        mimeType = content["mimeType"]
                    if "text" in content:
                        text = content["text"]
                    if "encoding" in content :
                        encoding = content["encoding"]

                    if size != "" and size != 0 :
                        extension = getFileExtension(mimeType)

                        orgFileName = getOrgFileName(url)
                        fileSaveName = genSaveName(orgFileName, extension, _prefix, keep)

                        if selection and selection != orgFileName:
                            continue

                        # verbose print
                        if listFiles:
                             loop = printFileList(fileSaveName, encoding, _prefix, allFiles, b64, nb64, fTypes, extension)
                             if loop:
                                 continue
                             _prefix+=1

                        # extract files
                        if not listFiles:
                            path = setFilePath(outPath)

                            if fTypes and extension in fTypes :
                                if encoding == "base64":
                                    with open(path + fileSaveName, "wb") as saveFile :
                                        saveFile.write(base64.decodebytes(text.encode()))
                                else:
                                    with open(path + fileSaveName, "w") as saveFile :
                                        saveFile.write(text)
                                _prefix+=1
                            elif encoding == "base64" and ( b64 or allFiles ) :
                                with open(path + fileSaveName, "wb") as saveFile :
                                    saveFile.write(base64.decodebytes(text.encode()))
                                _prefix+=1
                            elif not encoding and ( nb64 or allFiles ) :
                                with open(path + fileSaveName, "w") as saveFile :
                                    saveFile.write(text)
                                _prefix+=1


# calling main function
if __name__ ==  '__main__':
    main()
