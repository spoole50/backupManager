from bmHelper import *
import config

def processBackup():
    srcPath, targetPath = parseArgs()
    for subdir, dirs, files in os.walk(srcPath):
        for cFile in files:
            try:
                # Generate Full File Paths
                srcFile = os.path.join(subdir, cFile)
                targetSubdir = os.path.join(targetPath, os.path.relpath(subdir, srcPath))
                targetFile = os.path.join(targetSubdir, cFile)
                # targetFile = os.path.join(targetPath, os.path.relpath(os.path.join(subdir, cFile), srcPath))

                # Generate Current File Hash
                crc_hash, tSize = genHash(srcFile, config._RunStats['hashAlgo'], verbose=1)

                # Add to File Hash Dictionary
                if crc_hash not in config._RunStats['fileDict']:
                    config._RunStats['fileDict'][crc_hash] = [srcFile]
                else:
                    config._RunStats['fileDict'][crc_hash].append(srcFile)
                config._RunStats['totSize'] += tSize
                config._RunStats['totFiles'] += 1

                # os.makedirs(targetSubdir, exist_ok=True)
                # shutil.copy2(srcFullPath, targetFile)
                print(f"{'Source:': <13} {srcFile}\n{'OutputSubdir:': <13} {targetFile}\n")
            except OSError as oe:
                print(f"\n{oe}\n\nContinue to next file? (Y/N):", file=sys.stderr)
                if getYN():
                    continue
                else:
                    raise KeyboardInterrupt
            except Exception as e:
                print(f"WTF Happened Hurr:\n{e}")

def main():
    config.init()
    config._RunStats['start'] = timer()
    try:
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