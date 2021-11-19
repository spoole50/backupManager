import sys
import json
import argparse
import hashlib
import os
import pprint
from zlib import crc32
from datetime import timedelta, datetime
from timeit import default_timer as timer
import config as cg

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
    parser.add_argument('-o', '--outputLog',
                        type=str,
                        help='Output Path for log file')
    parser.add_argument('-d', '--dicts',
                        type=str,
                        help='Path to check for existing file/hash dicts')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Verbosity level (0-1), Default 0")
    parser.add_argument('-y', '--yes',
                        action='store_true',
                        help='Automatically Say YES to bypass any file errors (files w/errors will be skipped)')
    parser.add_argument('-dr', '--dryRun',
                        action='store_true',
                        help='Test current parameters and run operation printing source/destination without actual copy/move operation')
    parser.add_argument('-m', '--move',
                        action='store_true',
                        help='Move files instead of default copy behavior')
    parser.add_argument('-c', '--condense',
                        action='store_true',
                        help='Copy/move all files to root of target directory instead of default maintaining of file hierarchy')
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"ArgParse Error:\n{e}")
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
        lgFile = open(logPath, 'w')
        cg._RunStats['logFile'] = lgFile

        lgFile.write(f"""\n{datetime.now():%Y-%b-%d %H:%M:%S}
By User: {os.path.split(os.path.expanduser('~'))[-1]}\n\n""")

    except Exception as e:
        raise Exception(f"OpenLogFileError:\n{e}")

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
        try:
            os.makedirs(path, exist_ok=True)
        except:
            raise Exception(f"{path}\nNot a valid directory path, please try again")
    cg._RunStats['src'] = srcPath
    cg._RunStats['target'] = targetPath

    if args.algorithm is not None:
        cg._RunStats['hashAlgo'] = args.algorithm

    if args.outputLog is not None:
        initLog(os.path.abspath(args.outputLog))
    else:
        initLog(os.path.join(targetPath, f"bM_{datetime.now():%Y%m%d%H%M%S}.log"))
    
    # if args.dicts is not None:
    #     checkForDicts(os.path.abspath(args.dicts))
    # else:
    #     checkForDicts(srcPath)
    
    cg._RunStats['flags']['verbose'] = args.verbose
    cg._RunStats['flags']['yes'] = args.yes
    cg._RunStats['flags']['dry'] = args.dryRun
    cg._RunStats['flags']['move'] = args.move
    cg._RunStats['flags']['condense'] = args.condense
    return

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
    else:
        resHash = hex(resHash & 0xffffffff)
    
    logEvent(f"{resHash} - {sizeof_fmt(fSize)}")
    return str(resHash), fSize

def getYN():
    ans = input()
    if ans in ['Y', 'y']:
        return True
    else:
        return False

def sumReport(printDict=False):
    '''
    Generate copy/move operation summary report
    Sends formatted string to logging function

        Arguments:
            printDict (bool): Print file hash dicitonary. Mostly for debug/testing currently.
    '''
    totalTime = timedelta(seconds=timer() - cg._RunStats['start'])

    logEvent(f"""\n\nSummary Report:
    File Hash Algorithm: {cg._RunStats['hashAlgo']}
    Elapsed Time: {str(totalTime):10.10s}""")
    if cg._RunStats['totFiles'] and cg._RunStats['totSize']:
        logEvent(f"""
        -----Scan-----
        \tFiles Scanned: {cg._RunStats['totFiles']}
        \tTotal Size: {sizeof_fmt(cg._RunStats['totSize'])}
        ---Transfer---
        \tFiles Transfered: {cg._RunStats['totFiles_trans']} ({cg._RunStats['totFiles_trans']/cg._RunStats['totFiles'] * 100:.0f})%
        \tTotal Size Transfered: {sizeof_fmt(cg._RunStats['totSize_trans'])}
        \tAvg. Transfer Speed: {sizeof_fmt(cg._RunStats['totSize_trans']/totalTime.total_seconds())}/s
        """)
    else:
        logEvent(f"No Files Transferred")

    if printDict:
        print("\nFile Hash Dictionary:")
        pp = pprint.PrettyPrinter()
        pp.pprint(cg._RunStats['fileDict'])
    return

def logEvent(event):
    '''
    Add program operational events/errors to log and/or output

        Parameters:
            event (str): Formatted string detailing and event or error in program. Inserts into log file and prints if verbosity is enabled
    '''
    if cg._RunStats['logFile'] and not isinstance(cg._RunStats['logFile'], str):
        try:
            cg._RunStats['logFile'].write(event + '\n')
        except Exception as e:
            print(f"Event Logging Error:\n{e}")

    if cg._RunStats['flags']['verbose']:
        print(event)
    return

def endProgram():
    for dName in ['hashDict' ,'fileDict']:
        tDict = cg._RunStats[dName]
        if tDict:
            with open(os.path.join(cg._RunStats['target'], f"{dName}.json"), 'w') as outFile:
                json.dump(tDict, outFile)

    if cg._RunStats['logFile'] and not isinstance(cg._RunStats['logFile'], str):
            cg._RunStats['logFile'].close()
    return

def checkForDicts(path):
    if not os.path.isdir(path):
        path = cg._RunStats['src']
    for dName in ['hashDict' ,'fileDict']:
        dPath = os.path.join(path, f"{dName}.json")
        logEvent(f"Checking for JSON at {dPath}")
        if os.path.isfile(dPath):
            try:
                with open(dPath) as dFile:
                    tJson = json.load(dFile)
                cg._RunStats[dName] = tJson
                logEvent(f"Successfully Loaded {dName} dict from JSON")
            except Exception as e:
                logEvent(f"JSON Dict Load Error:\n{e}")
    return
