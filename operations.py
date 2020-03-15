##
# @file   operations.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module implements some of the instructions of IPPcode20


# This function returns the value and type of a variable
def get_var_value_type(data, identifier):
    tmp = identifier.split('@'); frame = tmp[0]; name = tmp[1]

    if frame == 'GF':
        if name in data.global_frame:
            var = data.global_frame[name]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in GF')

    elif frame == 'LF':
        if data.lf_index == -1: # cannot access a non-existent LF
            raise Exception(55, 'Nonexistent LF')

        if name in data.local_frame[data.lf_index]:
            var = data.local_frame[data.lf_index][name]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in LF')

    elif frame == 'TF':
        if not data.tf_defined: # cannot access a non-existent TF
            raise Exception(55, 'Nonexistent TF')

        if name in data.local_frame[data.lf_index + 1]:
            var = data.local_frame[data.lf_index + 1][name]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in TF')

    else: raise Exception(32, 'XML: Invalid frame') # this should not happen...

    var_type = var[0]; value = var[1]
    return value, var_type


# This function sets the value and type of a variable
def set_var_value_type(data, destination, value, var_type):
    tmp = destination.split('@'); frame = tmp[0]; name = tmp[1]

    if frame == 'GF':
        if name in data.global_frame:
            data.global_frame[name] = [var_type, value]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in GF')

    elif frame == 'LF':
        if data.lf_index == -1: # cannot access a non-existent LF
            raise Exception(55, 'Nonexistent LF')

        if name in data.local_frame[data.lf_index]:
            data.local_frame[data.lf_index][name] = [var_type, value]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in LF')

    elif frame == 'TF':
        if not data.tf_defined: # cannot access a non-existent TF
            raise Exception(55, 'Nonexistent TF')

        if name in data.local_frame[data.lf_index + 1]:
            data.local_frame[data.lf_index + 1][name] = [var_type, value]
        else:
            raise Exception(54, f'Nonexistent variable "{name}" in TF')

    else: raise Exception(32, 'XML: Invalid frame') # this should not happen...


# This class implements some  of the actual instructions of IPPcode20 as static methods.
# All the operations take an instance of the Processor class as an attribute (data) so that
# they can perform the desired operation all by themselves and all the the Processor has
# to do is to call one of these methods
class Operations:

    # Frames, variable declaration and initialization, function calls/returns
    @staticmethod
    def CREATEFRAME(data):
        if data.tf_defined:
            data.local_frame[data.lf_index + 1] = {} # overwrite the current TF
        else:
            data.local_frame.append({}) # create a new empty TF
            data.tf_defined = True

    @staticmethod
    def PUSHFRAME(data): # FIXME: pushframe when tf_defined is False????
        if data.tf_defined:
            data.lf_index += 1
            data.tf_defined = False
        else:
            raise Exception(55, 'PUSHFRAME: TF is not defined')

    @staticmethod
    def POPFRAME(data):
        if data.tf_defined:
            data.local_frame.pop() # delete the redundant temporary frame
        if data.lf_index = -1:
            raise Exception(55, 'POPFRAME: No available LF')
        data.lf_index -= 1

    @staticmethod
    def DEFVAR(data):
        var = data.instr[0].text.split('@'); frame = var[0]; name = var[1]

        if frame == 'GF':
            if name in data.global_frame:
                raise Exception(52, 'DEFVAR: Variable already defined in GF')
            else:
                data.global_frame[name] = [None, None] # [type=None, value=None]

        elif frame == 'LF':
            if name in data.local_frame[data.lf_index]:
                raise Exception(52, 'DEFVAR: Variable already defined in LF')
            else:
                data.local_frame[data.lf_index][name] = [None, None]

        elif frame == 'TF':
            if name in data.local_frame[data.lf_index + 1]:
                raise Exception(52, 'DEFVAR: Variable already defined in TF')
            else:
                data.local_frame[data.lf_index + 1][name] = [None, None]

        else: raise Exception(32, 'XML: Invalid frame') # this should not happen...

    @staticmethod
    def MOVE(data):
        try:
            # just check if the destination exists
            get_var_value_type(data, data.instr[0].text)

            # get the source symbol properties
            src = data.instr[1]
            src_type = src['type']

            # get the value and type of the source symbol
            if symb_type == 'var':
                src_value, src_var_type = get_var_value_type(data, src.text)
            else: 
                value_src = src.text
                src_var_type = src_type

            # write the value and type to the destination variable
            set_var_value_type(data, data.instr[0].text, src_value, src_var_type)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'MOVE: ' + msg)

    @staticmethod
    def CALL(data):
        data.ip_stack.append(data.ip + 1) # store the IP value

        label = data.instr.text
        if label in data.labels:
            data.ip = data.labels[label] # get the label position

        else:
            raise Exception(52, f'CALL: Label "{label}" is undefined')

    @staticmethod
    def RETURN(data):
        try:
            data.ip = data.ip_stack.pop()
        except:
            raise Exception(56, 'RETURN: Return address stack was empty')

    # Stack
    @staticmethod
    def PUSHS(data):
        pass

    @staticmethod
    def POPS():
        pass

    # Arithmethic, relation, boolean and conversion operations
    @staticmethod
    def ADD():
        pass

    @staticmethod
    def SUB():
        pass

    @staticmethod
    def MUL():
        pass

    @staticmethod
    def IDIV():
        pass

    @staticmethod
    def LT():
        pass

    @staticmethod
    def GT():
        pass

    @staticmethod
    def EQ():
        pass

    @staticmethod
    def AND():
        pass

    @staticmethod
    def OR():
        pass

    @staticmethod
    def NOT(): # 2 arguments!!!
        pass

    @staticmethod
    def INT2CHAR():
        pass

    @staticmethod
    def STRI2INT():
        pass

    # I/O
    @staticmethod
    def READ():
        pass

    @staticmethod
    def WRITE():
        pass

    # String manipulation
    @staticmethod
    def CONCAT():
        pass

    @staticmethod
    def STRLEN():
        pass

    @staticmethod
    def GETCHAR():
        pass

    @staticmethod
    def SETCHAR():
        pass

    # Type manipulation
    @staticmethod
    def TYPE():
        pass

    # Program flow control
    @staticmethod
    def LABEL():
        pass

    @staticmethod
    def JUMP():
        pass

    @staticmethod
    def JUMPIFEQ():
        pass

    @staticmethod
    def JUMPIFNEQ():
        pass

    @staticmethod
    def EXIT():
        pass

    # Debug
    @staticmethod
    def DPRINT():
        pass

    @staticmethod
    def BREAK():
        pass
