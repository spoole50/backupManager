import argparse
import sys
import os
import shutil
from zlib import crc32

def generateParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('SRC' ,
                        type=str,
                        help='Parent Folder to begin copy operation')
    parser.add_argument('TARGET',
                        type=str,
                        help='Destination for copy operation')
    args = parser.parse_args()
    return args

def genHash(fName):
    resHash = 0
    with open(fName, 'rb') as inFile:
        while True:
            read_data = inFile.read(25165824)
            if not read_data:
                break
            else:
                resHash = crc32(read_data, resHash)
    return resHash

def main():
    fileDict = {}
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)

    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            srcFile = os.path.join(subdir, cFile)
            targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
            # targetFile = os.path.join(targetPath, os.path.relpath(os.path.join(subdir, cFile), srcPath))
            targetFile = os.path.join(targetSubdir, cFile)
            crc_hash = genHash(srcFile)
            if crc_hash not in fileDict:
                fileDict[crc_hash] = [srcFile]
            else:
                fileDict[crc_hash].append(srcFile)
            # os.makedirs(targetSubdir, exist_ok=True)
            # shutil.copy2(srcFullPath, targetFile)
            # print(f"File: {crc_hash:x} - {srcFile}\n\tOutputSubdir: {targetSubdir}")
    print(fileDict)

if __name__ == '__main__':
    main()