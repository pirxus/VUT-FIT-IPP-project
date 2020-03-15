##
# @file   execute.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module performs the execution of the input program

from xml.etree import ElementTree as ET
from operations import Operations as op

# This class as an instruction processor and is responsible for the program execution
class Processor:
    def __init__(self, program, labels):
        self.program = program
        self.labels = labels

        self.ip_stack = [] # this list manages the return addresses for function calls
        self.global_frame = [] # a list of dictionaries of variables
        self.local_frame = []
        self.ip = 0
        self.global_frame_index = 0
        self.local_frame_index = 0


    def execute_program(self):
        # main processing loop
        while True:
            self.instr = program[ip] # load the next instruction
            try:
                self.process_instruction()
            except Exception as e:
                raise e

    def process_instruction(self):
        opcode = self.instr['opcode']
        
        try:
            if opcode == 'CREATEFRAME':
                op.CREATEFRAME()
            elif opcode == 'PUSHFRAME':
                op.PUSHFRAME()
            elif opcode == 'POPFRAME':
                op.POPFRAME()
            elif opcode == 'DEFVAR':
                op.DEFVAR()
            elif opcode == 'MOVE':
                op.MOVE()
            elif opcode == 'CALL':
                op.CALL()
            elif opcode == 'RETURN':
                op.RETURN()
            #####################
            elif opcode == 'PUSHS':
                op.PUSHS()
            elif opcode == 'POPS':
                op.POPS()
            #####################
            elif opcode == 'ADD':
                op.ADD()
            elif opcode == 'SUB':
                op.SUB()
            elif opcode == 'MUL':
                op.MUL()
            elif opcode == 'IDIV':
                op.IDIV()
            elif opcode == 'LT':
                op.LT()
            elif opcode == 'GT':
                op.GT()
            elif opcode == 'EQ':
                op.EQ()
            elif opcode == 'AND':
                op.AND()
            elif opcode == 'OR':
                op.OR()
            elif opcode == 'NOT':
                op.NOT()
            elif opcode == 'INT2CHAR':
                op.INT2CHAR()
            elif opcode == 'STRI2INT':
                op.STRI2INT()
            #####################
            elif opcode == 'READ':
                op.READ()
            elif opcode == 'WRITE':
                op.WRITE()
            #####################
            elif opcode == 'CONCAT':
                op.CONCAT()
            elif opcode == 'STRLEN':
                op.STRLEN()
            elif opcode == 'GETCHAR':
                op.GETCHAR()
            elif opcode == 'SETCHAR':
                op.SETCHAR()
            #####################
            elif opcode == 'TYPE':
                op.TYPE()
            #####################
            elif opcode == 'LABEL':
                pass
            elif opcode == 'JUMP':
                self.ip = op.JUMP(self.labels, self.instr[0])
                continue
            elif opcode == 'JUMPIFEQ':
                jump, index = op.JUMPIFEQ(self.labels, self.instr[0],
                        self.instr[1], self.instr[2])
                if jump:
                    self.ip = index
                continue
            elif opcode == 'JUMPIFNEQ':
                jump, index = op.JUMPIFNEQ(self.labels, self.instr[0],
                        self.instr[1], self.instr[2])
                if jump:
                    self.ip = index
            elif opcode == 'EXIT':
                retcode = op.EXIT(self.instr[0])
                sys.exit(retcode)
            #####################
            elif opcode == 'DPRINT':
                op.DPRINT()
            elif opcode == 'BREAK':
                op.BREAK()

            else:
                raise Exception

        except Exception as e:
            raise e
        self.ip += 1 # increment the instruction pointer
