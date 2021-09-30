import argparse
import sys
import os
import shutil
from zlib import crc32
import pprint
from timeit import default_timer as timer
from datetime import timedelta
import hashlib

_RunStats = {'start':0, 'totFiles':0, 'totSize':0, 'fileDict': {}}

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

def genHash(fName, hashAlgo='crc32', blockChunk=128, verbose=True):
    resHash = 0
    read_data = 1
    fSize = os.path.getsize(fName)
    if hashAlgo != 'crc32':
        _hash = hashlib.new(hashAlgo)
    with open(fName, 'rb') as inFile:
        while True:
            if not read_data:
                break
            elif hashAlgo == 'crc32':
                read_data = inFile.read(8192)
                resHash = crc32(read_data, resHash)
            else:
                read_data = inFile.read(_hash.block_size * blockChunk)
                _hash.update(read_data)
    if hashAlgo != 'crc32':
        resHash = _hash.hexdigest()
    if verbose:
        print(f"{resHash} - {sizeof_fmt(fSize)} - {fName}")
    return resHash, fSize

def processBackup():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)

    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            if _RunStats['totFiles'] < 10:
                srcFile = os.path.join(subdir, cFile)
                targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
                # targetFile = os.path.join(targetPath, os.path.relpath(os.path.join(subdir, cFile), srcPath))
                targetFile = os.path.join(targetSubdir, cFile)
                crc_hash, tSize = genHash(srcFile)
                if crc_hash not in _RunStats['fileDict']:
                    _RunStats['fileDict'][crc_hash] = [srcFile]
                else:
                    _RunStats['fileDict'][crc_hash].append(srcFile)
                _RunStats['totSize'] += tSize
                _RunStats['totFiles'] += 1
                # os.makedirs(targetSubdir, exist_ok=True)
                # shutil.copy2(srcFullPath, targetFile)
                # print(f"File: {crc_hash:x} - {srcFile}\n\tOutputSubdir: {targetSubdir}")   

def sumReport():
    pp = pprint.PrettyPrinter()
    _RunStats['end'] = timer()
    totalTime = timedelta(seconds=timer() - _RunStats['start'])

    print(f"""\n\nSummary Report:
    Elapsed Time: {str(totalTime):10.10s}
    Files Scanned: {_RunStats['totFiles']}
    Total Size: {sizeof_fmt(_RunStats['totSize'])}
    Avg. Tranfer Speed: {sizeof_fmt(_RunStats['totSize']/totalTime.total_seconds())}/s
    \nFiles Indexed:\n""")

    pp.pprint(_RunStats['fileDict'])

def main():
    _RunStats['start'] = timer()
    try:
        processBackup()
        sumReport()
    except OSError:
        print("Error ")
        print (OSError)
    except KeyboardInterrupt:
        sumReport()
    sys.exit(0)
        
        

if __name__ == '__main__':
    main()