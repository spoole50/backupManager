import argparse
import sys
import os
import shutil
from zlib import crc32
import pprint
from timeit import default_timer as timer
from datetime import timedelta

_RunStats = {'start':0, 'end':0, 'totFiles':0, 'totSize':0, 'fileDict': {}}

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

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def genHash(fName, verbose=True):
    resHash = 0
    fSize = os.path.getsize(fName)
    with open(fName, 'rb') as inFile:
        while True:
            read_data = inFile.read(25165824)
            if not read_data:
                break
            else:
                resHash = crc32(read_data, resHash)
    if verbose:
        print(f"{resHash} - {sizeof_fmt(fSize)} - {fName}")
    return resHash, fSize

def processBackup():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)

    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            
            srcFile = os.path.join(subdir, cFile)
            targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
            # targetFile = os.path.join(targetPath, os.path.relpath(os.path.join(subdir, cFile), srcPath))
            targetFile = os.path.join(targetSubdir, cFile)
            crc_hash, tSize = genHash(srcFile)
            _RunStats['totSize'] += tSize
            _RunStats['totFiles'] += 1
            if crc_hash not in _RunStats['fileDict']:
                _RunStats['fileDict'][crc_hash] = [srcFile]
            else:
                _RunStats['fileDict'][crc_hash].append(srcFile)
            # os.makedirs(targetSubdir, exist_ok=True)
            # shutil.copy2(srcFullPath, targetFile)
            # print(f"File: {crc_hash:x} - {srcFile}\n\tOutputSubdir: {targetSubdir}")   

def sumReport():
    pp = pprint.PrettyPrinter()
    _RunStats['end'] = timer()

    print(f"""\n\nSummary Report:
    Elapsed Time: {timedelta(seconds=_RunStats['end'] - _RunStats['start'])}
    Files Scanned: {_RunStats['totFiles']}
    Total Size: {sizeof_fmt(_RunStats['totSize'])}
    \nFiles Indexed:\n""")

    pp.pprint(_RunStats['fileDict'])

def main():
    _RunStats['start'] = timer()
    try:
        processBackup()
    except KeyboardInterrupt:
        sumReport()
        sys.exit(0)
    finally:
        sumReport()
        

if __name__ == '__main__':
    main()