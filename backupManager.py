import argparse
import sys
import os

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

def main():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    targetPath = os.path.abspath(args.TARGET)

    for subdir, dirs, files in os.walk(srcPath):
        for fle in files:
            print(os.path.join(subdir, fle))
            print(os.path.relpath(os.path.join(subdir, fle), srcPath))

if __name__ == '__main__':
    main()