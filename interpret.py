#!/usr/bin/python3
##
# @file   interpret.py
# @author Simon Sedlacek, xsedla1h
# @brief  This is the main module of the IPPcode20 interpreter

from xml.etree import ElementTree as ET
import sys

from xml_checks import *
from execute import execute_program

# TODO input check:
# - well-formed
# - check instruction elements + arguments for each instruction
# - sort by ascending order and check for duplicit order values
# - extract labels
# - start executing

NOT_WELL_FORMED = 31
XML_ERROR = 32 # pretty much all syntax, lexical and other input xml-fomat related errors

# get the input file name
if len(sys.argv) < 2: sys.exit(42)
filename = sys.argv[1]

try: check_well_formed(filename)
except Exception: sys.exit(NOT_WELL_FORMED)

program = ET.parse(filename).getroot()

try:
    program, labels = check_syntax(program)
    print(program, labels)

except Exception: sys.exit(XML_ERROR)

#try: execute_program(program, labels)
#except: sys.exit(42)

