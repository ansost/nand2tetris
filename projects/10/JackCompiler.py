symbols = ["}", "{", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
integer_constants = list(range(0,32767))

def return_token_type(token):
    if token in symbols:
        token_type = "symbol"
    elif token in keywords:
        token_type = "keyword"
    elif token in integer_constants:
        token_type = "IntegerConstant"
    elif token.startswith('"'):
        token_type = "StringConstant"
    else:
        token_type = "identifier"
    return token_type

def advance(current_idx):
    return current_idx+1

def write_token(xml_lines, token_list, current_idx):
    name = return_token_type(token_list[current_idx])
    xml_lines.append(f"<{name}> {token_list[current_idx]} </{name}>\n")
    current_idx = advance(current_idx)
    return xml_lines, current_idx

def write_partial_token(xml_lines, name = None, position=None):
    if position == "end":
        xml_lines.append(f"</{name}>\n")
    elif position == "beginning":
        xml_lines.append(f"<{name}>\n")
    else: 
        raise Exception("no vlaid position given in write partial token function.")
    return xml_lines

def compile_name(token_list, current_idx, xml_lines):
    """For className, varName and subroutineName."""
    if return_token_type(token_list[current_idx]) == "identifier":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    return token_list, current_idx, xml_lines

def compile_type(token_list, current_idx, xml_lines):
    if token_list[current_idx] in ["int", "char", "boolean"]:
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
        token_list, current_idx, xml_lines = compile_name(token_list, current_idx, xml_lines)
    else:
        raise Exception("Syntax Error!")
    return token_list, current_idx, xml_lines

def compile_classVarDec(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "classVarDec", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # static | field
    current_idx, xml_lines = compile_type(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_name(token_list, current_idx, xml_lines)
    #TODO make recursive bis ;
    if token_list[current_idx] == ",":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
        token_list, current_idx, xml_lines = compile_name(token_list, current_idx, xml_lines)
    elif token_list[current_idx] == ";":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "classVarDec", position="end")
    return current_idx, xml_lines

def compile_parameterList(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterList", position="beginning")
    if token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = compile_type(token_list, current_idx, xml_lines)
        print("Put recursive var name func here.")
    elif token_list[current_idx+1] != ")":
        raise Exception("Syntax Error!")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterList", position="end")
    return token_list, current_idx, xml_lines

def compile_varDec(token_list, current_idx, xml_lines):
    return token_list, current_idx, xml_lines

def compile_subroutineBody(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
    if token_list[current_idx] == "var":
        token_list, current_idx, xml_lines = compile_varDec(token_list, current_idx, xml_lines)
    else:
        raise Exception("Syntax Error!")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineBody", position="end")
    return token_list, current_idx, xml_lines

def compile_subroutineDec(token_list, current_idx):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineDec", position="beginning")
    if token_list[current_idx] in ["constructor", "function", "method"]:
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    
    if token_list[current_idx] == "void":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    elif token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = compile_type(token_list, current_idx, xml_lines)
    else:
        raise Exception("Syntax Error!")
    token_list, current_idx, xml_lines = compile_name(token_list, current_idx, xml_lines)

    if token_list[current_idx] == "(":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    
    if return_token_type(token_list[current_idx]) == ["int", "char", "boolean"]:
        compile_parameterList()
    else:
        raise Exception("Syntax Error!")
    
    if token_list[current_idx] == ")":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    
    if token_list[current_idx] == "{":
        token_list, current_idx, xml_lines = compile_subroutineBody(token_list, current_idx, xml_lines)
    else:
        raise Exception("Syntax Error!")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineDec", position="end")
    return token_list, current_idx, xml_lines

def compile_class(token_list, current_idx):
    xml_lines = ["<tokens>"]
    xml_lines, current_idx = write_partial_token(xml_lines, name = "class", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)

    if return_token_type(token_list[current_idx]) == "identifier":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    if token_list[current_idx] == "{":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    if token_list[current_idx] in ["static", "field"]:
        compile_classVarDec()
    elif token_list[current_idx] in ["constructor", "function", "method"]:
        compile_subroutineDec()
    elif token_list[current_idx] == "}":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    else:
        raise Exception("Syntax Error!")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "class", position="end")
    return xml_lines.append("</tokens>")