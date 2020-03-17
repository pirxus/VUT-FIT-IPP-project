#!/usr/bin/python3
##
# @file   interpret.py
# @author Simon Sedlacek, xsedla1h
# @brief  This is the main module of the IPPcode20 interpreter

from xml.etree import ElementTree as ET
import sys
import os
import getopt

from xml_checker import *
from execute import Processor

NOT_WELL_FORMED = 31
XML_ERROR = 32 # pretty much all syntax, lexical and other input xml-fomat related errors

# parse the interpret arguments
argv = sys.argv[1:]
try:
    args, __ = getopt.getopt(argv, '', longopts=['help', 'source=', 'input='])
except:
    sys.stderr.write('Unknown argument passed to the script\n')
    sys.exit(10)

source_file = None # variables holding our input and source filenames
input_file = None
for opt, val in args:
    if opt == '--help':
        if len(args) == 1: # print help
            print('Program načte XML reprezentaci programu a tento program s využitím vstupu dle parametrů příkazové řádky interpretuje a generuje výstup.')
            sys.exit(0)
        else:
            sys.stderr.write('Invalid argument combination passed to the script\n')
            sys.exit(10)
    elif opt == '--source':
        source_file = val
    elif opt == '--input':
        input_file = val

try:
    if source_file == None and input_file == None:
        sys.stderr.write('At least one of the options "input" or '
            '"source" has to be specified\n')
        sys.exit(10)
    elif source_file == None:
        source_file = sys.stdin
        input_file = open(input_file)
    elif input_file == None:
        input_file = sys.stdin
        source_file = open(source_file)
    else:
        input_file = open(input_file)
        source_file = open(source_file)
except:
        sys.stderr.write('Could not open input or source file\n')
        sys.exit(11)

# parse the xml and perform basic analysis (well-formed)
try:
    program = ET.parse(source_file).getroot()
except:
    sys.stderr.write(f'Source file {source_file.name} is not a well-formed XML\n')
    sys.exit(NOT_WELL_FORMED)

# perform the syntax and lexical analysis (plus some semantic checks) of the program
try:
    program, labels = check_syntax(program)
except Exception as e:
    sys.stderr.write(str(e.args) + '\n')
    sys.exit(XML_ERROR)

# now execute the program
processor = Processor(program, labels, input_file)
try:
    processor.execute_program()
except Exception as e:
    retcode, message = e.args
    sys.stderr.write(message + '\n')
    sys.exit(retcode)
