##
# @file   execute.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module performs the execution of the input program

ip_stack = [] # this list manages the return addresses for function calls
global_frame = {}
local_frame = {}
tmp_frame = {}
labels = {}

def execute_program(program, labels):
    ip = 0 # instruction pointer
