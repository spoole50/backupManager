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
    '''
    Defines program arguments and generates argumentParser object

        Returns:
            args (argparse.ArgumentParser): Argument parser with all defined arguments
    '''
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
    '''
    Validate and initialie logging file

        Parameters:
            logPath (str): Path name or location for log file
    '''
    if os.path.isdir(logPath):
        logPath = os.path.join(logPath, 'bM.log')
    try:
        lgFile = open(logPath, 'a+')
        config._RunStats['logFile'] = lgFile

        lgFile.write(f"""\n{datetime.now():%Y-%b-%d %H:%M:%S}
By User: {os.path.split(os.path.expanduser('~'))[-1]}\n\n""")

    except Exception as e:
        print(f"OpenLogFileError:\n{e}")
        raise KeyboardInterrupt

def parseArgs():
    '''
    Parse program arguments
        Validate and set SRC and TARGET paths
        Set appropriate global variables/flags based on arguments

        Return:
            srcPath (str): Source file path for files to be copied/moved. Refered to as SRC in arguments
            targetPath (str): Target file path for destination of copy/move operation. Refered to as TARGET in arguments
    '''
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)
    for path in [srcPath, targetPath]:
        if not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
            except:
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

    return srcPath, targetPath

def sizeof_fmt(num):
    '''
    Format File Sizes

        Parameters:
            num (int/float): Base file size in bytes

        Returns:
            (str): Formatted, human readable file size string
    '''
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]: 
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}B"
        num /= 1024.0
    return f"{num:.1f}YiB"

def genHash(fName, hashAlgo, blockChunk=128, verbose=None):
    '''
    Generate formatted file hash

        Arguments:
            fName (str): File name to be hashed
            hashAlgo (str): Name of hash algorithm to be used
            blockChunk (int): 
    '''
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
    
    logEvent(f"{resHash} - {sizeof_fmt(fSize)}")
    return resHash, fSize

def getYN():
    ans = input()
    if ans in ['Y', 'y']:
        return True
    else:
        return False

def sumReport(printDict=False):
    '''
    Generate copy/move operation summary report

        Arguments:
            printDict (bool): Print file hash dicitonary. Mostly for debug/testing currently. Sends formatted string to logging function
    '''
    totalTime = timedelta(seconds=timer() - config._RunStats['start'])

    logEvent(f"""\n\nSummary Report:
    File Hash Algorithm: {config._RunStats['hashAlgo']}
    Elapsed Time: {str(totalTime):10.10s}
    -----Scan-----
    \tFiles Scanned: {config._RunStats['totFiles']}
    \tTotal Size: {sizeof_fmt(config._RunStats['totSize'])}
    ---Transfer---
    \tFiles Transfered: {config._RunStats['totFiles_trans']} ({config._RunStats['totFiles_trans']/config._RunStats['totFiles'] * 100:.0f})%
    \tTotal Size Transfered: {sizeof_fmt(config._RunStats['totSize_trans'])}
    \tAvg. Transfer Speed: {sizeof_fmt(config._RunStats['totSize_trans']/totalTime.total_seconds())}/s
    """)

    if printDict:
        print("\nFile Hash Dictionary:")
        pp = pprint.PrettyPrinter()
        pp.pprint(config._RunStats['fileDict'])

def logEvent(event):
    '''
    Add program operational events/errors to log and/or output

        Parameters:
            event (str): Formatted string detailing and event or error in program. Inserts into log file and prints if verbosity is enabled
    '''
    try:
        config._RunStats['logFile'].write(event + '\n')
    except Exception as e:
        print(f"Event Logging Error:\n{e}")

    if config._RunStats['flags']['verbose']:
        print(event)
