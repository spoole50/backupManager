import argparse
import sys
import os
import shutil
from zlib import crc32
import pprint
from timeit import default_timer as timer
from datetime import timedelta
import hashlib

_RunStats = {'start':0,
            'totFiles':0,
            'totSize':0,
            'hashAlgo':'crc32',
            'fileDict': {},
            'flags':{
                'move':0
            }}

def generateParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('SRC' ,
                        type=str,
                        help='Parent Folder to begin copy operation')
    parser.add_argument('TARGET',
                        type=str,
                        help='Destination for copy operation')
    parser.add_argument('-a', '--algorithm',
                        type=str,
                        help='Algorithm to utilize for generation of file hashes')
    args = parser.parse_args()
    return args

def parseArgs():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)
    if args.algorithm is not None:
        _RunStats['hashAlgo'] = args.algorithm
    return srcPath, targetPath

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]: 
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def genHash(fName, hashAlgo, blockChunk=128, verbose=None):
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
    if verbose == 1:
        print(f"{resHash} - {sizeof_fmt(fSize)}")
    if verbose == 2:
        print(f"{resHash} - {sizeof_fmt(fSize)} - {fName}")
    return resHash, fSize

def getYN():
    ans = input()
    if ans in ['Y', 'y']:
        return True
    else:
        return False

def processBackup():
    srcPath, targetPath = parseArgs()
    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            try:
                srcFile = os.path.join(subdir, cFile)
                targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
                # targetFile = os.path.join(targetPath, os.path.relpath(os.path.join(subdir, cFile), srcPath))
                targetFile = os.path.join(targetSubdir, cFile)
                crc_hash, tSize = genHash(srcFile, _RunStats['hashAlgo'], verbose=1)
                if crc_hash not in _RunStats['fileDict']:
                    _RunStats['fileDict'][crc_hash] = [srcFile]
                else:
                    _RunStats['fileDict'][crc_hash].append(srcFile)
                _RunStats['totSize'] += tSize
                _RunStats['totFiles'] += 1
                # os.makedirs(targetSubdir, exist_ok=True)
                # shutil.copy2(srcFullPath, targetFile)
                print(f"{'Source:': <13} {srcFile}\n{'OutputSubdir:': <13} {targetFile}\n")
            except OSError as oe:
                print(f"\n{oe}\n\nContinue to next file? (Y/N):")
                if getYN():
                    continue
                else:
                    raise KeyboardInterrupt
            except Exception as e:
                print(f"WTF Happened Hurr:\n{e}")
                

def sumReport(printDict=False):
    totalTime = timedelta(seconds=timer() - _RunStats['start'])

    print(f"""\n\nSummary Report:
    Elapsed Time: {str(totalTime):10.10s}
    Files Scanned: {_RunStats['totFiles']}
    Total Size: {sizeof_fmt(_RunStats['totSize'])}
    Avg. Tranfer Speed: {sizeof_fmt(_RunStats['totSize']/totalTime.total_seconds())}/s
    File Hash Algorithm: {_RunStats['hashAlgo']}
    """)

    if printDict:
        print("\nFile Hash Dictionary:")
        pp = pprint.PrettyPrinter()
        pp.pprint(_RunStats['fileDict'])

def main():
    _RunStats['start'] = timer()
    try:
        parseArgs()
        processBackup()
        sumReport()
    except OSError as e:
        sumReport()
        print("\nOS Error:")
        print (e)
    except KeyboardInterrupt:
        sumReport()
    sys.exit(0)
        
        

if __name__ == '__main__':
    main()