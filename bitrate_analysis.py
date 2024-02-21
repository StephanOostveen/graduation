#!/usr/bin/env python3

import argparse
import json
import os
import math

def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def standardIDMax(frame):
    databits = 8*frame['sizeInBytes']
    return 34+databits+13 + math.floor((34+databits-1)/4)

def standardIDMin(frame):
    databits = 8*frame['sizeInBytes']
    return 34+databits+13

def extendedIDMax(frame):
    databits = 8*frame['sizeInBytes']
    return 54+databits+13 + math.floor((54+databits-1)/4)

def extendedIDMin(frame):
    databits = 8*frame['sizeInBytes']
    return 54+databits+13

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('canjson', type=file_path)
    args = parser.parse_args()
    file = args.canjson

    with open(file, 'r') as jsonfile:
        jsonarray = json.load(jsonfile)
        bps_max = 0
        bps_min = 0
        count = 0
        for frame in jsonarray:
            count += 1 / frame['interval']
            if frame["canID"] < 2 ** 11:
                bps_max += standardIDMax(frame) * (1 / frame['interval'])
                bps_min += standardIDMin(frame) * (1 / frame['interval'])
            else:
                bps_max += extendedIDMax(frame) * (1 / frame['interval'])
                bps_min += extendedIDMin(frame) * (1 / frame['interval'])
        print('{} has a min requirement of {} bits/second'.format(file,bps_min))
        print('{} has a max requirement of {} bits/second'.format(file,bps_max))
        print('Sending {} frames per second'.format(count))