def write_push(segment, index):
    return f"push {segment} {index}"

def write_pop(segment, index):
    """Segment can be: ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
    index has to be an integer"""
    return f"pop {segment} {index}"

def write_arithmetic(command):
    """command can be: add, sub, neg, eq, gt, lt, and, or, not"""
    lookup = {
    '+': 'ADD',
    '-': 'SUB',
    '=': 'EQ',
    '>': 'GT',
    '<': 'LT',
    '&': 'AND',
    '|': 'OR'
  }
    return f"{lookup[command]}\n"

def write_label(label):
    return f"label {label}"

def write_goto(label):
    return f"goto {label}"

def write_if(label):
    return

def write_routineCall(routineName, nArgs):
    return f"call {routineName} {nArgs}"

def write_functionCall(functionName, nVars):
    return f"function {functionName} {nVars}"

def write_return():
    return f"return\n"
