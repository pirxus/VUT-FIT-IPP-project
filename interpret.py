#!/usr/bin/python3
##
# @file   interpret.py
# @author Simon Sedlacek, xsedla1h
# @brief  This is the main module of the IPPcode20 interpreter

from xml.etree import ElementTree as ET
import sys

from xml_checker import *
from execute import Processor

NOT_WELL_FORMED = 31
XML_ERROR = 32 # pretty much all syntax, lexical and other input xml-fomat related errors

#TODO: program arguments, syntax checking, 

# get the input file name TODO: proper argument parsing
if len(sys.argv) < 2: sys.exit(42)
filename = sys.argv[1]

# check if the input xml is well-formed
try: check_well_formed(filename)
except Exception: sys.exit(NOT_WELL_FORMED)

program = ET.parse(filename).getroot()

# perform the syntax and lexical analysis (plus some semantic checks) of the program
try:
    program, labels = check_syntax(program)
except Exception:
    sys.exit(XML_ERROR)

# now execute the program
processor = Processor(program, labels)
try:
    processor.execute_program()
except Exception as e:
    retcode, message = e.args
    sys.stderr.write(message + '\n')
    sys.exit(retcode)
