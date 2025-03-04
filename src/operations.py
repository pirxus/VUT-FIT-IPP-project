##
# @file   operations.py
# @author Simon Sedlacek, xsedla1h
# @brief  This module implements some of the instructions of IPPcode20


# This function returns the value and type of a variable
def get_var_type_value(data, identifier):
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
    return var_type, value


# This function sets the value and type of a variable
def set_var_type_value(data, destination, var_type, value):
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


# This function returns the type and value of a symbol
def get_symbol_type_value(data, symbol):
    symbol_type = symbol.attrib['type']
    symbol_value = symbol.text

    # if the symbol is a variable, get its type and value
    if symbol_type == 'var':
        try: 
            symbol_type, symbol_value = get_var_type_value(data, symbol_value)
        except Exception as e:
            raise e

    return symbol_type, symbol_value


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
    def PUSHFRAME(data):
        if data.tf_defined:
            data.lf_index += 1
            data.tf_defined = False
        else:
            raise Exception(55, 'PUSHFRAME: TF is not defined')

    @staticmethod
    def POPFRAME(data):
        if data.tf_defined:
            data.local_frame.pop() # delete the redundant temporary frame
        if data.lf_index == -1:
            raise Exception(55, 'POPFRAME: No available LF')
        data.lf_index -= 1
        data.tf_defined = True

    @staticmethod
    def DEFVAR(data):
        var = data.instr[0].text.split('@'); frame = var[0]; name = var[1]

        if frame == 'GF':
            if name in data.global_frame:
                raise Exception(52, 'DEFVAR: Variable already defined in GF')
            else:
                data.global_frame[name] = [None, None] # [type=None, value=None]

        elif frame == 'LF':
            if data.lf_index == -1:
                raise Exception(55, 'DEFVAR: LF does not exist')
            if name in data.local_frame[data.lf_index]:
                raise Exception(52, 'DEFVAR: Variable already defined in LF')
            else:
                data.local_frame[data.lf_index][name] = [None, None]

        elif frame == 'TF':
            if not data.tf_defined:
                raise Exception(55, 'DEFVAR: TF is undefined')
            if name in data.local_frame[data.lf_index + 1]:
                raise Exception(52, 'DEFVAR: Variable already defined in TF')
            else:
                data.local_frame[data.lf_index + 1][name] = [None, None]

        else: raise Exception(32, 'XML: Invalid frame') # this should not happen...

    @staticmethod
    def MOVE(data):
        try:
            # just check if the destination exists
            get_var_type_value(data, data.instr[0].text)

            # get the source symbol type and value and write them to the destination
            src_type, src_value = get_symbol_type_value(data, data.instr[1])
            if src_type == None:
                raise Exception(56, 'Uninitialized symbol')
            set_var_type_value(data, data.instr[0].text, src_type, src_value)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'MOVE: ' + msg)

    @staticmethod
    def CALL(data):
        data.ip_stack.append(data.ip + 1) # store the IP value

        label = data.instr[0].text
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
        try:
            # get the symbol type and value
            src_type, src_value = get_symbol_type_value(data, data.instr[0])
            if src_type == None:
                raise Exception(56, 'Uninitialized symbol')
        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'PUSHS: ' + msg)

        # ... and push them onto the data stack
        data.data_stack.append((src_type, src_value))

    @staticmethod
    def POPS(data):
        try:
            src_type, src_value = data.data_stack.pop()
        except:
            raise Exception(56, 'POPS: Data stack was empty')

        try:
            set_var_type_value(data, data.instr[0].text, src_type, src_value)
        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'POPS: ' + msg)

    @staticmethod
    def CLEARS(data):
        # clear the data stack
        data.data_stack.clear()

    # Arithmethic, relation, boolean and conversion operations
    @staticmethod
    def ADD(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, op1_type,
                        op1_value + op2_value) 
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'ADD: ' + msg)

    @staticmethod
    def ADDS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # ... and push the result of the operation onto the data stack
                data.data_stack.append((op1_type, op1_value + op2_value))
            elif op1_type == None or op2_type == None: # this should probably not happen..
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'ADDS: ' + msg)

    @staticmethod
    def SUB(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, op1_type,
                        op1_value - op2_value) 
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'SUB: ' + msg)

    @staticmethod
    def SUBS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # ... and push the result of the operation onto the data stack
                data.data_stack.append((op1_type, op1_value - op2_value))
            elif op1_type == None or op2_type == None: # this should probably not happen..
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'SUBS: ' + msg)

    @staticmethod
    def MUL(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, op1_type,
                        op1_value * op2_value) 
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'MUL: ' + msg)

    @staticmethod
    def MULS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types
            if ((op1_type == 'int' and op2_type == 'int') or
                    (op1_type == 'float' and op2_type == 'float')):
                # ... and push the result of the operation onto the data stack
                data.data_stack.append((op1_type, op1_value * op2_value))
            elif op1_type == None or op2_type == None: # this should probably not happen..
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int" or "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'MULS: ' + msg)

    @staticmethod
    def IDIV(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == 'int' and op2_type == 'int':
                if op2_value == 0:
                    raise Exception(57, 'Division by zero')
                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, 'int',
                        op1_value // op2_value) 
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'IDIV: ' + msg)

    @staticmethod
    def IDIVS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types
            if op1_type == 'int' and op2_type == 'int':
                # ... and push the result of the operation onto the data stack
                data.data_stack.append((op1_type, op1_value // op2_value))
            elif op1_type == None or op2_type == None: # this should probably not happen..
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "int"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'IDIVS: ' + msg)

    @staticmethod
    def DIV(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == 'float' and op2_type == 'float':
                if op2_value == 0:
                    raise Exception(57, 'Division by zero')
                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, 'float',
                        op1_value / op2_value) 
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'DIV: ' + msg)

    @staticmethod
    def DIVS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == 'float' and op2_type == 'float':
                if op2_value == 0:
                    raise Exception(57, 'Division by zero')
                # write the result of the operation
                data.data_stack.append((op1_type, op1_value / op2_value))
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Both operands must be of type "float"')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'DIVS: ' + msg)

    @staticmethod
    def LT(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type and op1_type != 'nil':
                # perform the comparison
                if op1_type in ['int', 'string', 'float']:
                    result = 'true' if op1_value < op2_value else 'false'
                elif op1_type == 'bool':
                    if op1_value == 'false' and op2_value == 'true': result = 'true'
                    else: result = 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, 'bool', result)
            else:
                raise Exception(53, 'Operands incompatible for comparison')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'LT: ' + msg)

    @staticmethod
    def LTS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type and op1_type != 'nil':
                # perform the comparison
                if op1_type in ['int', 'string', 'float']:
                    result = 'true' if op1_value < op2_value else 'false'
                elif op1_type == 'bool':
                    if op1_value == 'false' and op2_value == 'true': result = 'true'
                    else: result = 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

                # push the result back onto the stack
                data.data_stack.append(('bool', result))
            else:
                raise Exception(53, 'Operands incompatible for comparison')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'LTS: ' + msg)

    @staticmethod
    def GT(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type and op1_type != 'nil':
                # perform the comparison
                if op1_type in ['int', 'string', 'float']:
                    result = 'true' if op1_value > op2_value else 'false'
                elif op1_type == 'bool':
                    if op1_value == 'true' and op2_value == 'false': result = 'true'
                    else: result = 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

                # write the result of the operation
                set_var_type_value(data, data.instr[0].text, 'bool', result)
            else:
                raise Exception(53, 'Operands incompatible for comparison')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'GT: ' + msg)

    @staticmethod
    def GTS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type and op1_type != 'nil':
                # perform the comparison
                if op1_type in ['int', 'string', 'float']:
                    result = 'true' if op1_value > op2_value else 'false'
                elif op1_type == 'bool':
                    if op1_value == 'true' and op2_value == 'false': result = 'true'
                    else: result = 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

                # push the result back onto the stack
                data.data_stack.append(('bool', result))
            else:
                raise Exception(53, 'Operands incompatible for comparison')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'GTS: ' + msg)

    @staticmethod
    def EQ(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            if op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'bool', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'EQ: ' + msg)

    @staticmethod
    def EQS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            if op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # push the result back onto the stack
            data.data_stack.append(('bool', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'EQS: ' + msg)

    @staticmethod
    def AND(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == 'bool' and  op2_type == 'bool':

                # perform the operation
                if op1_value == 'true' and op2_value == 'true': result = 'true'
                else: result = 'false'
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'bool', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'AND: ' + msg)

    @staticmethod
    def ANDS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == 'bool' and  op2_type == 'bool':

                # perform the operation
                if op1_value == 'true' and op2_value == 'true': result = 'true'
                else: result = 'false'
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # push the result back onto the stack
            data.data_stack.append(('bool', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'ANDS: ' + msg)

    @staticmethod
    def OR(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == 'bool' and  op2_type == 'bool':

                # perform the operation
                if op1_value == 'true' or op2_value == 'true': result = 'true'
                else: result = 'false'
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'bool', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'OR: ' + msg)

    @staticmethod
    def ORS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == 'bool' and  op2_type == 'bool':

                # perform the operation
                if op1_value == 'true' or op2_value == 'true': result = 'true'
                else: result = 'false'
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # push the result back onto the stack
            data.data_stack.append(('bool', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'ORS: ' + msg)

    @staticmethod
    def NOT(data):
        try:
            # get the operand type and value
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # check operand types and other constraints
            if op_type == 'bool':

                # perform the operation
                result = 'false' if op_value == 'true' else 'true'
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'bool', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'NOT: ' + msg)

    @staticmethod
    def NOTS(data):
        try:
            # get the operand type and value
            try: op_type, op_value = data.data_stack.pop()
            except: raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op_type == 'bool':

                # perform the operation
                result = 'false' if op_value == 'true' else 'true'
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Operands incompatible for logical operation')

            # push the result back onto the stack
            data.data_stack.append(('bool', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'NOTS: ' + msg)

    @staticmethod
    def INT2CHAR(data):
        try:
            # get the operand type and value
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # check operand types and other constraints
            if op_type == 'int':
                try: char = chr(op_value)
                except: raise Exception(58, 'Invalid ordinal value')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be an integer')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'string', char)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'INT2CHAR: ' + msg)

    @staticmethod
    def INT2CHARS(data):
        try:
            # get the operand type and value
            try: op_type, op_value = data.data_stack.pop()
            except: raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op_type == 'int':
                try: char = chr(op_value)
                except: raise Exception(58, 'Invalid ordinal value')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be an integer')

            # push the result back onto the stack
            data.data_stack.append(('string', char))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'INT2CHARS: ' + msg)

    @staticmethod
    def STRI2INT(data):
        try:
            # get the value and type of the operands
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check the operand types and store the char present on the specified position
            if op1_type == 'string' and op2_type == 'int':
                limit = len(op1_value)

                if not (0 <= op2_value < limit):
                    raise Exception(58, 'Index out of range')

                set_var_type_value(data, data.instr[0].text, 'int',
                        ord(op1_value[op2_value]))
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'STRI2INT: ' + msg)

    @staticmethod
    def STRI2INTS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check the operand types and store the char present on the specified position
            if op1_type == 'string' and op2_type == 'int':
                limit = len(op1_value)

                if not (0 <= op2_value < limit):
                    raise Exception(58, 'Index out of range')

                # push the result back onto the stack
                data.data_stack.append(('int', ord(op1_value[op2_value])))

            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'STRI2INTS: ' + msg)

    @staticmethod
    def INT2FLOAT(data):
        try:
            # get the operand type and value
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # check operand types and other constraints
            if op_type == 'int':
                try: result = float(op_value)
                except: raise Exception(58, 'Could not convert int to float')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be an integer')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'float', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'INT2FLOAT: ' + msg)

    @staticmethod
    def INT2FLOATS(data):
        try:
            # get the operand type and value
            try: op_type, op_value = data.data_stack.pop()
            except: raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op_type == 'int':
                try: result = float(op_value)
                except: raise Exception(58, 'Could not convert int to float')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be an integer')

            # push the result back onto the stack
            data.data_stack.append(('float', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'INT2FLOATS: ' + msg)

    @staticmethod
    def FLOAT2INT(data):
        try:
            # get the operand type and value
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # check operand types and other constraints
            if op_type == 'float':
                try: result = int(op_value)
                except: raise Exception(58, 'Could not convert float to int')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be a float')

            # write the result of the operation
            set_var_type_value(data, data.instr[0].text, 'int', result)

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'FLOAT2INT: ' + msg)

    @staticmethod
    def FLOAT2INTS(data):
        try:
            # get the operand type and value
            try: op_type, op_value = data.data_stack.pop()
            except: raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op_type == 'float':
                try: result = int(op_value)
                except: raise Exception(58, 'Could not convert float to int')
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Second operand has to be a float')

            # push the result back onto the stack
            data.data_stack.append(('int', result))

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'FLOAT2INTS: ' + msg)

    # I/O
    @staticmethod
    def READ(data):
        try:
            # get the value and type of the operands
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # check the operand types and store the char present on the specified position
            if op_type == 'type' and op_value in ['int', 'string', 'bool', 'float']:
                read = data.input_file.readline() # read one line of input
                if read == '':
                    op_value = 'nil'
                    read = 'nil'
                else:
                    if read[-1] == '\n': read = read[:-1] # cut the trailing newline
                    if op_value == 'int':
                        try: read = int(read)
                        except: read = 'nil'; op_value = 'nil'
                    elif op_value == 'string':
                        read = str(read)
                    elif op_value == 'float':
                        try: read = float.fromhex(read)
                        except: read = 'nil'; op_value = 'nil'
                    else: # bool
                        if read.casefold() == 'true': read = 'true'
                        else: read = 'false'

                set_var_type_value(data, data.instr[0].text, op_value, read)
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'READ: ' + msg)

    @staticmethod
    def WRITE(data):
        try:
            # get the value and type of the symbol
            op_type, op_value = get_symbol_type_value(data, data.instr[0])
            if op_type == 'nil':
                op_value = ''
            elif op_type in ['int', 'string', 'bool']:
                pass
            elif op_type == 'float': # convert floats back to hexa
                op_value = float.hex(op_value)
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')
            
            # print out the symbol value
            print(op_value, end='')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'WRITE: ' + msg)

    # String manipulation
    @staticmethod
    def CONCAT(data):
        try:
            # get the value and type of the symbol
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # concatenate the strings
            if op1_type == 'string' and op2_type == 'string':
                set_var_type_value(data, data.instr[0].text, 'string',
                        op1_value + op2_value)
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'CONCAT: ' + msg)

    @staticmethod
    def STRLEN(data):
        try:
            # get the value and type of the symbol
            op_type, op_value = get_symbol_type_value(data, data.instr[1])

            # store the string length
            if op_type == 'string':
                set_var_type_value(data, data.instr[0].text, 'int', len(op_value))
            elif op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'STRLEN: ' + msg)

    @staticmethod
    def GETCHAR(data):
        try:
            # get the value and type of the operands
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check the operand types and store the char present on the specified position
            if op1_type == 'string' and op2_type == 'int':
                limit = len(op1_value)

                if not (0 <= op2_value < limit):
                    raise Exception(58, 'Index out of range')

                set_var_type_value(data, data.instr[0].text, 'string',
                        op1_value[op2_value])
            elif op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'GETCHAR: ' + msg)

    @staticmethod
    def SETCHAR(data):
        try:
            # get the value and type of the operands
            var_type, var_value = get_var_type_value(data, data.instr[0].text)
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check the operand types and store the char present on the specified position
            if var_type == 'string' and op1_type == 'int' and op2_type == 'string':
                limit = len(var_value)

                # check the constraints
                if not (0 <= op1_value < limit) or len(op2_value) == 0:
                    raise Exception(58, 'Index out of range')

                var_value = var_value[:op1_value] + op2_value[0] + var_value[op1_value+1:]
                set_var_type_value(data, data.instr[0].text, 'string', var_value)
            elif op1_type == None or op2_type == None or var_type == None:
                raise Exception(56, 'Uninitialized symbol')
            else:
                raise Exception(53, 'Invalid operand type')

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'SETCHAR: ' + msg)

    # Type manipulation
    @staticmethod
    def TYPE(data):
        try:
            op_type, op_value = get_symbol_type_value(data, data.instr[1])
            if op_type == None or op_value == None:
                op_value = ''
                op_type = 'string'
            elif op_type in ['int', 'string', 'bool', 'nil', 'float']:
                op_value = op_type
                op_type = 'string'
            else:
                raise Exception(53, 'Invalid operand type')

            # write the type to the variable
            set_var_type_value(data, data.instr[0].text, op_type, op_value)
            
        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'TYPE: ' + msg)

    # Program flow control
    @staticmethod
    def LABEL():
        pass

    @staticmethod
    def JUMP(data):
        label = data.instr[0].text
        if label in data.labels:
            data.ip = data.labels[label] # get the label position
        else:
            raise Exception(52, f'JUMP: Label "{label}" is undefined')

    @staticmethod
    def JUMPIFEQ(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # test the label existence
            label = data.instr[0].text
            if label not in data.labels:
                raise Exception(52, f'Label "{label}" is undefined')

            # perform the jump
            if result == 'true':
                data.ip = data.labels[label] # get the label position
                return True
            else:
                return False # let the processor know the jump will take place

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'JUMPIFEQ: ' + msg)

    @staticmethod
    def JUMPIFEQS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # test the label existence
            label = data.instr[0].text
            if label not in data.labels:
                raise Exception(52, f'Label "{label}" is undefined')

            # perform the jump
            if result == 'true':
                data.ip = data.labels[label] # get the label position
                return True
            else:
                return False # let the processor know the jump will take place

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'JUMPIFEQS: ' + msg)

    @staticmethod
    def JUMPIFNEQ(data):
        try:
            # get the operand types and values
            op1_type, op1_value = get_symbol_type_value(data, data.instr[1])
            op2_type, op2_value = get_symbol_type_value(data, data.instr[2])

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            if op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # test the label existence
            label = data.instr[0].text
            if label not in data.labels:
                raise Exception(52, f'Label "{label}" is undefined')

            # perform the jump
            if result == 'false':
                data.ip = data.labels[label] # get the label position
                return True
            else:
                return False # let the processor know the jump will take place

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'JUMPIFNEQ: ' + msg)

    @staticmethod
    def JUMPIFNEQS(data):
        try:
            try:
                # get the operand types and values
                op2_type, op2_value = data.data_stack.pop()
                op1_type, op1_value = data.data_stack.pop()
            except:
                raise Exception(56, 'Empty data stack')

            # check operand types and other constraints
            if op1_type == None or op2_type == None:
                raise Exception(56, 'Uninitialized symbol')
            if op1_type == op2_type:

                # perform the comparison
                if op1_type in ['int', 'string', 'bool', 'nil', 'float']:
                    result = 'true' if op1_value == op2_value else 'false'
                else:
                    raise Exception(53, 'Operands incompatible for comparison')

            elif op1_type == 'nil' or op2_type == 'nil':
                result = 'false'
            else:
                raise Exception(53, 'Operands incompatible for comparison')

            # test the label existence
            label = data.instr[0].text
            if label not in data.labels:
                raise Exception(52, f'Label "{label}" is undefined')

            # perform the jump
            if result == 'false':
                data.ip = data.labels[label] # get the label position
                return True
            else:
                return False # let the processor know the jump will take place

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'JUMPIFNEQS: ' + msg)

    @staticmethod
    def EXIT(data):
        try:
            op_type, retcode = get_symbol_type_value(data, data.instr[0])
            if op_type == None:
                raise Exception(56, 'Uninitialized symbol')
            elif op_type != 'int':
                raise Exception(53, 'Invalid return code type')
            elif retcode < 0 or retcode > 49 or not isinstance(retcode, int):
                raise Exception(57, 'Invalid return code')
            return retcode

        except Exception as e:
            retcode, msg = e.args
            raise Exception(retcode, 'EXIT: ' + msg)

    # Debug
    @staticmethod
    def DPRINT(data):
        pass

    @staticmethod
    def BREAK(data):
        pass
