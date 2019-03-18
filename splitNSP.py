#!/usr/bin/env python3
# Author: AnalogMan
# Modified Date: 2018-10-08
# Purpose: Splits Nintendo Switch NSP files into parts for installation on FAT32

import os
import argparse
import shutil
from datetime import datetime
startTime = datetime.now()

splitSize = 0xFFFF0000 # 4,294,901,760 bytes
chunkSize = 0x8000 # 32,768 bytes

def splitQuick(filepath):
    fileSize = os.path.getsize(filepath)
    info = shutil.disk_usage(os.path.dirname(os.path.abspath(filepath)))
    if info.free < splitSize:
        print('Not enough temporary space. Needs 4GiB of free space\n')
        return
    print('Calculating number of splits...\n')
    splitNum = int(fileSize/splitSize)
    if splitNum == 0:
        print('This NSP is under 4GiB and does not need to be split.\n')
        return

    print('Splitting NSP into {0} parts...\n'.format(splitNum + 1))
    
    # Create directory, delete if already exists
    dir = filepath[:-4] + '_split.nsp'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    # Move input file to directory and rename it to first part
    filename = os.path.basename(filepath)
    shutil.move(filepath, os.path.join(dir, '00'))
    filepath = os.path.join(dir, '00')

    # Calculate size of final part to copy first
    finalSplitSize = fileSize - (splitSize * splitNum)

    # Copy final part and trim from main file
    with open(filepath, 'r+b') as nspFile:
        nspFile.seek(finalSplitSize * -1, os.SEEK_END)
        outFile = os.path.join(dir, '{:02}'.format(splitNum))
        partSize = 0
        print('Starting part {:02}'.format(splitNum))
        with open(outFile, 'wb') as splitFile:
            while partSize < finalSplitSize:
                splitFile.write(nspFile.read(chunkSize))
                partSize += chunkSize
        nspFile.seek(finalSplitSize * -1, os.SEEK_END)
        nspFile.truncate()
        print('Part {:02} complete'.format(splitNum))

    # Loop through additional parts and trim
    with open(filepath, 'r+b') as nspFile:
        for i in range(splitNum - 1):
            nspFile.seek(splitSize * -1, os.SEEK_END)
            outFile = os.path.join(dir, '{:02}'.format(splitNum - (i + 1)))
            partSize = 0
            print('Starting part {:02}'.format(splitNum - (i + 1)))
            with open(outFile, 'wb') as splitFile:
                 while partSize < splitSize:
                    splitFile.write(nspFile.read(chunkSize))
                    partSize += chunkSize
            nspFile.seek(splitSize * -1, os.SEEK_END)
            nspFile.truncate()
            print('Part {:02} complete'.format(splitNum - (i + 1)))
    
    # Print assurance statement for user
    print('Starting part 00\nPart 00 complete')

    print('\nNSP successfully split!\n')
    
def splitCopy(filepath, output_dir=""):
    fileSize = os.path.getsize(filepath)
    info = shutil.disk_usage(os.path.dirname(os.path.abspath(filepath)))
    if info.free < fileSize*2:
        print('Not enough free space to run. Will require twice the space as the NSP file\n')
        return
    print('Calculating number of splits...\n')
    splitNum = int(fileSize/splitSize)
    if splitNum == 0:
        print('This NSP is under 4GiB and does not need to be split.\n')
        return
    
    print('Splitting NSP into {0} parts...\n'.format(splitNum + 1))

    # Create directory, delete if already exists
    if output_dir == "":
        dir = filepath[:-4] + '_split.nsp'
    else:
        if output_dir[-4:] != '.nsp':
            output_dir+= ".nsp"
        dir = output_dir
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    remainingSize = fileSize

    # Open source file and begin writing to output files stoping at splitSize
    with open(filepath, 'rb') as nspFile:
        for i in range(splitNum + 1):
            partSize = 0
            print('Starting part {:02}'.format(i))
            outFile = os.path.join(dir, '{:02}'.format(i))
            with open(outFile, 'wb') as splitFile: 
                if remainingSize > splitSize:
                    while partSize < splitSize:
                        splitFile.write(nspFile.read(chunkSize))
                        partSize += chunkSize
                    remainingSize -= splitSize
                else:
                    while partSize < remainingSize:
                        splitFile.write(nspFile.read(chunkSize))
                        partSize += chunkSize
            print('Part {:02} complete'.format(i))
    print('\nNSP successfully split!\n')

def main():
    print('\n========== NSP Splitter ==========\n')

    # Arg parser for program options
    parser = argparse.ArgumentParser(description='Split NSP files into FAT32 compatible sizes')
    parser.add_argument('filepath', help='Path to NSP file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quick', action='store_true', help='Splits file in-place without creating a copy. Only requires 4GiB free space to run')
    group.add_argument('-o', '--output-dir', type=str, default="",
                        help="Set alternative output dir")

    # Check passed arguments
    args = parser.parse_args()

    filepath = args.filepath

    # Check if required files exist
    if os.path.isfile(filepath) == False:
        print('NSP cannot be found\n')
        return 1
    
    # Split NSP file
    if args.quick:
        splitQuick(filepath)
    else:
        splitCopy(filepath, args.output_dir)

if __name__ == "__main__":
    main()
