#!/usr/bin/python3

from xml.etree import ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys

NOT_WELL_FORMED = 31
XML_ERROR = 32 # pretty much all syntax, lexical and other xml-related errors

# get the input file name
if len(sys.argv) < 2: sys.exit(42)
filename = sys.argv[1]

# check the input file well-formed-ness
try:
    well_formed_parser = make_parser()
    well_formed_parser.setContentHandler(ContentHandler())
    well_formed_parser.parse(filename)
except Exception:
    sys.stderr.write(f'Input file {filename} is not a well-formed XML\n')
    sys.exit(NOT_WELL_FORMED)

program = ET.parse(filename).getroot()

def check_syntax(program):
    if program.tag != 'program' or 'language' not in program.attrib or\
            program.attrib['language'] != 'IPPcode20':
        sys.stderr.write('Invalid root element\n')
        sys.exit(XML_ERROR)

    order = 1
    for instr in program:
        if instr.tag != 'instruction':
            sys.stderr.write('Invalid top level element tag')
            
        if int(instr.attrib['order']) != order:
            sys.stderr.write('Invalid order number %d of instruction %s\n'
                    % (instr.attrib['order'], instr.attrib['opcode']))
            sys.exit(XML_ERROR)
        order += 1

ip_stack = [] # this list manages the return addresses for function calls
global_frame = {}
local_frame = {}
tmp_frame = {}
labels = {}

check_syntax(program)
