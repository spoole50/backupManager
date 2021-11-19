from argparse import ArgumentError
from ctypes import resize
import shutil
from typing import SupportsComplex

from bmHelper import *
import config as cg

def processBackup():
    srcPath = rs['src']
    targetPath = rs['target']
    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            try:
                # Generate Full File Paths
                srcFile = os.path.join(subdir, cFile)
                if rs['flags']['condense']:
                    targetSubdir = targetPath
                else:
                    targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
                targetFile = os.path.join(targetSubdir, cFile)

                # Generate Current File Hash
                crc_hash, tSize = genHash(srcFile, rs['hashAlgo'], verbose=1)

                # Add to File Hash Dictionary
                if crc_hash not in rs['hashDict']:
                    rs['hashDict'][crc_hash] = [srcFile]
                    if not rs['flags']['dry']:
                        if rs['flags']['move']:
                            os.makedirs(targetSubdir, exist_ok=True)
                            print("mv")
                            shutil.move(srcFile, targetFile)
                        else:
                            os.makedirs(targetSubdir, exist_ok=True)
                            shutil.copy2(srcFile, targetFile)
                    rs['totSize_trans'] += tSize
                    rs['totFiles_trans'] += 1
                else:
                    rs['hashDict'][crc_hash].append(srcFile)
                rs['fileDict'][srcFile] = crc_hash
                rs['totSize'] += tSize
                rs['totFiles'] += 1
                logEvent(f"{'Source:': <13} {srcFile}\n{'Target:': <13} {targetFile}\n")
            except OSError as oe:
                logEvent(f"OS Error\nSrcFile: {srcFile}:\n\n{oe}")
                print(f"\n{oe}\n\nContinue to next file? (Y/N):", file=sys.stderr)
                if rs['flags']['yes'] or getYN():
                    continue
                else:
                    raise KeyboardInterrupt
            except Exception as e:
                print(f"WTF Happened Hurr:\n{e}")

def main():
    cg.init()
    global rs
    rs = cg._RunStats
    rs['start'] = timer()
    try:
        parseArgs()
        processBackup()
    except OSError as e:
        print("\nOS Error:")
        print (e)
    except KeyboardInterrupt:
        pass 
    finally:
        sumReport()
        endProgram()
        
if __name__ == '__main__':
    main()