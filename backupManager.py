from argparse import ArgumentError
import shutil

from bmHelper import *
import config

def processBackup(srcPath, targetPath):
    initLog(config._RunStats['logFile'])
    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            try:
                # Generate Full File Paths
                srcFile = os.path.join(subdir, cFile)
                targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
                targetFile = os.path.join(targetSubdir, cFile)

                # Generate Current File Hash
                crc_hash, tSize = genHash(srcFile, config._RunStats['hashAlgo'], verbose=1)

                # Add to File Hash Dictionary
                if crc_hash not in config._RunStats['hashDict']:
                    config._RunStats['hashDict'][crc_hash] = [srcFile]
                    config._RunStats['fileDict'][srcFile] = crc_hash
                    if not config._RunStats['flags']['dry']:
                        os.makedirs(targetSubdir, exist_ok=True)
                        shutil.copy2(srcFile, targetFile)
                    config._RunStats['totSize_trans'] += tSize
                    config._RunStats['totFiles_trans'] += 1
                else:
                    config._RunStats['hashDict'][crc_hash].append(srcFile)
                    config._RunStats['fileDict'][srcFile] = crc_hash
                config._RunStats['totSize'] += tSize
                config._RunStats['totFiles'] += 1
                logEvent(f"{'Source:': <13} {srcFile}\n{'OutputSubdir:': <13} {targetFile}\n")
            except OSError as oe:
                logEvent(f"OS Error\nSrcFile: {srcFile}:\n\n{oe}")
                print(f"\n{oe}\n\nContinue to next file? (Y/N):", file=sys.stderr)
                if config._RunStats['flags']['yes'] or getYN():
                    continue
                else:
                    raise KeyboardInterrupt
            except Exception as e:
                print(f"WTF Happened Hurr:\n{e}")

def main():
    config.init()
    config._RunStats['start'] = timer()
    try:
        processBackup(*parseArgs())
    except OSError as e:
        print("\nOS Error:")
        print (e) 
    finally:
        sumReport()
        if config._RunStats['logFile'] and not isinstance(config._RunStats['logFile'], str):
            config._RunStats['logFile'].close()
        
if __name__ == '__main__':
    main()