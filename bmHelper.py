import argparse
import hashlib
import os
from zlib import crc32
from datetime import timedelta
from timeit import default_timer as timer
from globals import _RunStats

def generateParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('SRC' ,
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
    args = parser.parse_args()
    return args

def parseArgs():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)

    if args.algorithm is not None:
        _RunStats['hashAlgo'] = args.algorithm
    if args.logOutput is not None:
        _RunStats['logFilePath'] = os.path.abspath(args.logOutput)
    else:
        _RunStats['logFilePath'] = os.path.join(targetPath, 'bM.log')
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

def sumReport(printDict=False):
    totalTime = timedelta(seconds=timer() - _RunStats['start'])

    print(f"""\n\nSummary Report:
    Elapsed Time: {str(totalTime):10.10s}
    Files Scanned: {_RunStats['totFiles']}
    Total Size: {sizeof_fmt(_RunStats['totSize'])}
    Avg. Transfer Speed: {sizeof_fmt(_RunStats['totSize']/totalTime.total_seconds())}/s
    File Hash Algorithm: {_RunStats['hashAlgo']}
    """)

    if printDict:
        print("\nFile Hash Dictionary:")
        pp = pprint.PrettyPrinter()
        pp.pprint(_RunStats['fileDict'])