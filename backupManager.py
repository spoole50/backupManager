import argparse
import sys
import os

def generateParse():
    parser = argparse.ArgumentParser()
    parser.add_argument('SRC' ,
                        type=str,
                        help='Parent Folder to begin copy operation')
    args = parser.parse_args()
    return args

def main():
    args = generateParse()
    srcPath = os.path.abspath(args.SRC)
    print(srcPath)

if __name__ == '__main__':
    main()