import sys
import argparse
import hashlib
import os
import pprint
from zlib import crc32
from datetime import timedelta, datetime
from timeit import default_timer as timer
import config

def generateParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('SRC',
                        type=str,
                        help='Parent Folder Path to begin copy operation')
    parser.add_argument('TARGET',
                        type=str,
                        help='Destination Path for copy/move operation')
    parser.add_argument('-a', '--algorithm',
                        type=str,
                        help='Algorithm to utilize for generation of file hashes')
    parser.add_argument('-o', '--logOutput',
                        type=str,
                        help='Output Path for log file')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Verbosity level (0-1), Default 0")
    parser.add_argument('-y', '--yes',
                        action='store_true',
                        help="Automatically Say YES to bypass any file errors (files will be skipped)")
    args = parser.parse_args()
    return args

def initLog(logPath):
    try:
        lgFile = open(logPath, 'a+')
        config._RunStats['logFile'] = lgFile

        lgFile.write(f"""\n{datetime.now():%Y-%b-%d %H:%M:%S}
By User: {os.path.split(os.path.expanduser('~'))[-1]}\n\n""")

    except Exception as e:
        print(f"OpenLogFileError:\n{e}")
        raise KeyboardInterrupt

def parseArgs():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)
    for path in [srcPath, targetPath]:
        if not os.path.isdir(path):
            print(f"{path}\nNot a valid directory path, please try again")
            raise KeyboardInterrupt

    if args.algorithm is not None:
        config._RunStats['hashAlgo'] = args.algorithm

    if args.logOutput is not None:
        initLog(os.path.abspath(args.logOutput))
    else:
        initLog(os.path.join(targetPath, 'bM.log'))
    
    config._RunStats['flags']['verbose'] = args.verbose
    config._RunStats['flags']['yes'] = args.yes
    # if args.verbose:
    #     config._RunStats['flags']['verbose'] = int(args.verbose)
    # else:
    #     config._RunStats['flags']['verbose'] = 0

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
                read_data = inFile.read(1048576)
                resHash = crc32(read_data, resHash)
            else:
                read_data = inFile.read(_hash.block_size * blockChunk)
                _hash.update(read_data)
    if hashAlgo != 'crc32':
        resHash = _hash.hexdigest()
    
    logEvent(f"{resHash} - {sizeof_fmt(fSize)} - {fName}")
    return resHash, fSize

def getYN():
    ans = input()
    if ans in ['Y', 'y']:
        return True
    else:
        return False

def sumReport(printDict=False):
    totalTime = timedelta(seconds=timer() - config._RunStats['start'])

    logEvent(f"""\n\nSummary Report:
    Elapsed Time: {str(totalTime):10.10s}
    Files Scanned: {config._RunStats['totFiles']}
    Total Size: {sizeof_fmt(config._RunStats['totSize'])}
    Avg. Transfer Speed: {sizeof_fmt(config._RunStats['totSize']/totalTime.total_seconds())}/s
    File Hash Algorithm: {config._RunStats['hashAlgo']}
    """)

    if printDict:
        print("\nFile Hash Dictionary:")
        pp = pprint.PrettyPrinter()
        pp.pprint(config._RunStats['fileDict'])

def logEvent(event):
    try:
        config._RunStats['logFile'].write(event + '\n')
    except Exception as e:
        print(f"Event Logging Error:\n{e}")

    if config._RunStats['flags']['verbose']:
        print(event)
