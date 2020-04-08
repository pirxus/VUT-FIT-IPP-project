##
# @file   execute.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module performs the execution of the input program

from xml.etree import ElementTree as ET
from operations import Operations as op
import sys

# This class as an instruction processor and is responsible for the program execution
class Processor:
    def __init__(self, program, labels, input_file):
        self.input_file = input_file # user input file
        self.program = program
        self.labels = labels

        self.data_stack = []
        self.ip_stack = [] # this list manages the return addresses for function calls
        self.global_frame = {} # a dictionary of variables in the GF
        self.local_frame = [] # a list of dictionaries of variables for each LF
        self.ip = 0
        self.gf_index = 0
        self.lf_index = -1
        self.tf_defined = False # indicates the existence of a temporary frame


    def execute_program(self):
        # main processing loop
        program_len = len(self.program)
        while self.ip < program_len:
            self.instr = self.program[self.ip] # load the next instruction
            try:
                self.process_instruction()
            except Exception as e:
                raise e

    def process_instruction(self):
        opcode = self.instr.attrib['opcode']
        try:
            if opcode == 'CREATEFRAME':
                op.CREATEFRAME(self)
            elif opcode == 'PUSHFRAME':
                op.PUSHFRAME(self)
            elif opcode == 'POPFRAME':
                op.POPFRAME(self)
            elif opcode == 'DEFVAR':
                op.DEFVAR(self)
            elif opcode == 'MOVE':
                op.MOVE(self)
            elif opcode == 'CALL':
                op.CALL(self); return
            elif opcode == 'RETURN':
                op.RETURN(self); return
            #####################
            elif opcode == 'PUSHS':
                op.PUSHS(self)
            elif opcode == 'POPS':
                op.POPS(self)
            elif opcode == 'CLEARS':
                op.CLEARS(self)
            #####################
            elif opcode == 'ADD':
                op.ADD(self)
            elif opcode == 'ADDS':
                op.ADDS(self)
            elif opcode == 'SUB':
                op.SUB(self)
            elif opcode == 'SUBS':
                op.SUBS(self)
            elif opcode == 'MUL':
                op.MUL(self)
            elif opcode == 'MULS':
                op.MULS(self)
            elif opcode == 'IDIV':
                op.IDIV(self)
            elif opcode == 'IDIVS':
                op.IDIVS(self)
            elif opcode == 'DIV':
                op.DIV(self)
            elif opcode == 'DIVS':
                op.DIV(self)
            elif opcode == 'LT':
                op.LT(self)
            elif opcode == 'LTS':
                op.LTS(self)
            elif opcode == 'GT':
                op.GT(self)
            elif opcode == 'GTS':
                op.GTS(self)
            elif opcode == 'EQ':
                op.EQ(self)
            elif opcode == 'EQS':
                op.EQS(self)
            elif opcode == 'AND':
                op.AND(self)
            elif opcode == 'ANDS':
                op.ANDS(self)
            elif opcode == 'OR':
                op.OR(self)
            elif opcode == 'ORS':
                op.ORS(self)
            elif opcode == 'NOT':
                op.NOT(self)
            elif opcode == 'NOTS':
                op.NOTS(self)
            elif opcode == 'INT2CHAR':
                op.INT2CHAR(self)
            elif opcode == 'INT2CHARS':
                op.INT2CHARS(self)
            elif opcode == 'STRI2INT':
                op.STRI2INT(self)
            elif opcode == 'STRI2INTS':
                op.STRI2INTS(self)
            elif opcode == 'INT2FLOAT':
                op.INT2FLOAT(self)
            elif opcode == 'FLOAT2INT':
                op.FLOAT2INT(self)
            elif opcode == 'INT2FLOATS':
                op.INT2FLOAT(self)
            elif opcode == 'FLOAT2INTS':
                op.FLOAT2INT(self)
            #####################
            elif opcode == 'READ':
                op.READ(self)
            elif opcode == 'WRITE':
                op.WRITE(self)
            #####################
            elif opcode == 'CONCAT':
                op.CONCAT(self)
            elif opcode == 'STRLEN':
                op.STRLEN(self)
            elif opcode == 'GETCHAR':
                op.GETCHAR(self)
            elif opcode == 'SETCHAR':
                op.SETCHAR(self)
            #####################
            elif opcode == 'TYPE':
                op.TYPE(self)
            #####################
            elif opcode == 'LABEL':
                op.LABEL()
            elif opcode == 'JUMP':
                op.JUMP(self); return
            elif opcode == 'JUMPIFEQ':
                if op.JUMPIFEQ(self): return
            elif opcode == 'JUMPIFEQS':
                if op.JUMPIFEQS(self): return
            elif opcode == 'JUMPIFNEQ':
                if op.JUMPIFNEQ(self): return
            elif opcode == 'JUMPIFNEQS':
                if op.JUMPIFNEQS(self): return
            elif opcode == 'EXIT':
                retcode = op.EXIT(self); sys.exit(retcode)
            #####################
            elif opcode == 'DPRINT':
                op.DPRINT(self)
            elif opcode == 'BREAK':
                op.BREAK(self)

            else:
                raise Exception(32, 'Unknown opcode') # this should not happen...

        except Exception as e:
            raise e
        self.ip += 1 # increment the instruction pointer
