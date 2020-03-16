##
# @file   xml_checker.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module implements functions used for checking the integrity of the
#         input xml for the interpreter


from xml.etree import ElementTree as ET
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import re

# check the syntax and lexical format of an instruction element
def check_instructions(root):
    for instr in root:
        try:
            check_instruction(instr)
        except Exception as e:
            sys.stderr.write(str(ET.tostring(instr)))
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

    # now classify the instruction and then check its args according to the class
    # of instructions it fits in based on the number of arguments..
    opcode = instr.attrib['opcode']

    # before checking the arguments, sort the in ascending order (arg1, arg2, ...)
    instr[:] = sorted(instr, key=lambda child: child.tag)

    if opcode in ['MOVE', 'NOT', 'INT2CHAR', 'STRLEN', 'TYPE']: # var, symb
        if len(instr) == 2 and instr[0].tag == 'arg1' and instr[1].tag == 'arg2':
            if ArgChecks.check_var(instr[0]) and ArgChecks.check_symbol(instr[1]):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['DEFVAR', 'POPS']: # var
        if len(instr) == 1 and instr[0].tag == 'arg1':
            if ArgChecks.check_var(instr[0]):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['PUSHS', 'WRITE', 'EXIT', 'DPRINT']: # symb
        if len(instr) == 1 and instr[0].tag == 'arg1':
            if ArgChecks.check_symbol(instr[0]):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['CALL', 'LABEL', 'JUMP']: # label
        if len(instr) == 1 and instr[0].tag == 'arg1':
            if ArgChecks.check_label(instr[0]):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT','GT', 'EQ',
            'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR']: # var, symb, symb
        if (len(instr) == 3 and instr[0].tag == 'arg1' and
                instr[1].tag == 'arg2' and instr[2].tag == 'arg3'):
            if (ArgChecks.check_var(instr[0]) and ArgChecks.check_symbol(instr[1]) and
                    ArgChecks.check_symbol(instr[2])):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['READ']: # var, type
        if len(instr) == 2 and instr[0].tag == 'arg1' and instr[1].tag == 'arg2':
            if ArgChecks.check_var(instr[0]) and ArgChecks.check_arg_type(instr[1]):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['JUMPIFEQ', 'JUMPIFNEQ']: # label, symb, symb
        if (len(instr) == 3 and instr[0].tag == 'arg1' and
                instr[1].tag == 'arg2' and instr[2].tag == 'arg3'):
            if (ArgChecks.check_label(instr[0]) and ArgChecks.check_symbol(instr[1]) and
                    ArgChecks.check_symbol(instr[2])):
                return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    elif opcode in ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']: # ...
        if len(instr) == 0:
            return True
        raise Exception(f'Invalid {opcode} attributes', instr.attrib['order'])

    else:
        raise Exception('Unknown opcode', opcode)


# extracts all the labels and returns them in a dictionary along with their order numbers
def get_labels(root):
    labels = {}
    for instr in root:
        if instr.attrib['opcode'] == 'LABEL':

            if instr[0].text in labels:
                sys.stderr.write('Label redefinition\n')
                sys.exit(52) #FIXME: proper exception propagation
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


class ArgChecks:

    # specific argument types
    @staticmethod
    def check_arg_int(arg):
        if (len(arg.attrib) == 1 and 'type' in arg.attrib and
                arg.attrib['type'] == 'int'):
            try: arg.text = int(arg.text)
            except: return False # not a valid integer
            return True
        return False

    @staticmethod
    def check_arg_string(arg):
        if (len(arg.attrib) == 1 and 'type' in arg.attrib and
                arg.attrib['type'] == 'string'):
            try: arg.text = str(arg.text)
            except:
                return False # not a valid string
            return True
        return False

    @staticmethod
    def check_arg_bool(arg):
        if (len(arg.attrib) == 1 and 'type' in arg.attrib and
                arg.attrib['type'] == 'bool'):
            if arg.text not in ['true', 'false']: return False # not a valid bool
            return True
        return False

    @staticmethod
    def check_arg_nil(arg):
        if (len(arg.attrib) == 1 and 'type' in arg.attrib and
                arg.attrib['type'] == 'nil'):
            if arg.text != 'nil': return False # not a valid nil@nil
            return True
        return False

    @staticmethod
    def check_arg_type(arg):
        if (len(arg.attrib) == 1 and 'type' in arg.attrib and
                arg.attrib['type'] == 'type'):
            if arg.text not in ['int', 'string', 'bool']:
                return False # not a valid type specification
            return True
        return False

    # general argument types
    @staticmethod
    def check_var(var):
        if (len(var.attrib) == 1 and 'type' in var.attrib and
                var.attrib['type'] == 'var'):
            var_name_match = re.compile(r'^((GF)|(LF)|(TF))@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$')
            if re.fullmatch(var_name_match, var.text) == None:
                return False # invalid variable name
            return True
        return False

    @staticmethod
    def check_symbol(symbol):
        # a symbol is a variable or a literal...
        if (ArgChecks.check_var(symbol) or 
                ArgChecks.check_arg_int(symbol) or
                ArgChecks.check_arg_string(symbol) or
                ArgChecks.check_arg_nil(symbol) or
                ArgChecks.check_arg_bool(symbol)):
            return True
        return False

    @staticmethod
    def check_label(label):
        if (len(label.attrib) == 1 and 'type' in label.attrib and
                label.attrib['type'] == 'label'):
            label_name_match = re.compile(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$')
            if re.fullmatch(label_name_match, label.text) == None:
                return False # invalid variable name
            return True
        return False
