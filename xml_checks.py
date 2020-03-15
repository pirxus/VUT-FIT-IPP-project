##
# @file   xml_checks.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module implements functions used for checking the integrity of the
#         input xml for the interpreter


from xml.etree import ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys

# check the syntax and lexical format of an instruction element
def check_instructions(root):
    for instr in root:
        try:
            check_instruction(instr)
        except Exception as e:
            raise e


# checks a single instruction format
def check_instruction(instr):
    if (instr.tag != 'instruction' or
            set(instr.attrib.keys()) != {'opcode', 'order'}):
        raise Exception('Invalid top level element/instruction format')
    
    # check the order attribute format and value
    try:
        order = int(instr.attrib['order'])
        if order < 1:
            raise Exception('Invalid order attribute value', order)
    except ValueError:
        raise Exception('Invalid order attribute format', instr.attrib['order'])

    return None

    # now classify the instruction and then check its format according to the class
    # of instructions it fits in based on the number of arguments..
    opcode = instr.attrib['opcode']
    if opcode in []:
        pass
    elif opcode in []:
        pass
    elif opcode in []:
        pass
    elif opcode in []:
        pass
    elif opcode in []:
        pass
    elif opcode in []:
        pass
    else:
        raise Exception('Unknown opcode', opcode)


# extracts all the labels and returns them in a dictionary along with their order numbers
def get_labels(root):
    labels = {}
    for instr in root:
        if instr.attrib['opcode'] == 'LABEL':

            if instr[0].text in labels: #FIXME is this the correct way to access an arg??
                raise Exception('Label redefinition', instr[0].text) # Label redefinition

            labels[instr[0].text] = instr.attrib['order'] # add the new label to the dict
    return labels


# checks the order number integrity among the instructions and returns an ordered
# list of instructions that can be iterated over and therefore executed as code
def order_instructions(root):
    # sort the instructions by order number
    root[:] = sorted(root, key=lambda child: int(child.get('order')))
    for instr in root:
        instr[:] = sorted(instr, key=lambda child: child.tag)

    # now check for duplicit order values
    counter = 0
    last = -1 
    for instr in root:
        order = int(instr.attrib['order'])
        if order < counter + 1 or order == last :
            raise Exception('Duplicit or invalid order attribute', order)

        # now let's rewrite the order numbers so that they correspond to the indexes
        # of the instructions in the ordered list
        last = order 
        instr.attrib['order'] = counter
        counter += 1

    return root


def check_syntax(program):
    if (program.tag != 'program' or 'language' not in program.attrib or
            program.attrib['language'] != 'IPPcode20' or
            set(program.attrib.keys()) - {'language', 'name', 'description'} != set()):
        sys.stderr.write('Invalid root element\n') 
        sys.exit(XML_ERROR)
    
    try:
        check_instructions(program) # check the instruction formats
        ordered = order_instructions(program) # order the instructions
        labels = get_labels(program) # extract the labels

    except Exception as e:
        sys.stderr.write(e)
        raise e

    return ordered, labels


# check the xml file well-formed-ness
def check_well_formed(filename):
    try:
        well_formed_parser = make_parser()
        well_formed_parser.setContentHandler(ContentHandler())
        well_formed_parser.parse(filename)
    except Exception:
        sys.stderr.write(f'Input file {filename} is not a well-formed XML\n')
        raise Exception
