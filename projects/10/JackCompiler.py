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
    return xml_lines

# def compile_name(token_list, current_idx, xml_lines):
#     """For className, varName and subroutineName."""
#     if return_token_type(token_list[current_idx]) == "identifier":
#         xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
#     return token_list, current_idx, xml_lines

def compile_type(token_list, current_idx, xml_lines):
    if token_list[current_idx] in ["int", "char", "boolean"]:
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
        token_list, current_idx, xml_lines = compile_name(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_varName(token_list, current_idx, xml_lines, use_compile_type = None):
    if use_compile_type:
        token_list, current_idx, xml_lines = compile_type(token_list, current_idx, xml_lines)

    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write varName
    if token_list[current_idx+1] == ";":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write semicolon
        return token_list, current_idx, xml_lines
    if token_list[current_idx+1] == ",":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write comma
        compile_varName(token_list, current_idx, xml_lines, use_compile_type)

def compile_classVarDec(token_list, current_idx, xml_lines):
    if token_list[current_idx+1] in ["constructor", "function", "method"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines, current_idx = write_partial_token(xml_lines, name = "classVarDec", position="beginning")
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write static | field
        xml_lines, current_idx = compile_type(xml_lines, token_list, current_idx) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines, current_idx = write_partial_token(xml_lines, name = "classVarDec", position="end")
        compile_classVarDec(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_varDec(token_list, current_idx, xml_lines):
    if token_list[current_idx+1] in ["let", "if", "while", "do", "return"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines, current_idx = write_partial_token(xml_lines, name = "VarDec", position="beginning")
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write var
        xml_lines, current_idx = compile_type(xml_lines, token_list, current_idx) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines, current_idx = write_partial_token(xml_lines, name = "VarDec", position="end")
        compile_varDec(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_parameterList(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterList", position="beginning")
    token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = True)
    xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterList", position="end")
    return token_list, current_idx, xml_lines

def compile_expression(xml_lines, token_list, current_idx):
    return xml_lines, token_list, current_idx #TODO

def compile_let(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "letStatement", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write let
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write varName   
    if token_list[current_idx] == "[":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write [
        xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write ]
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write =   
    xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
    xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx) # write ;
    write_partial_token(xml_lines, name = "letStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_ifwhile(token_list, current_idx, xml_lines, name = ""):
    write_partial_token(xml_lines, name = f"{name}Statement", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write (
    xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write )
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write {
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write }
    if token_list[current_idx] == "else":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write else
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write {
        token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write }
    write_partial_token(xml_lines, name = f"{name}Statement", position="end")
    return token_list, current_idx, xml_lines

def compile_subroutineCall(xml_lines, token_list, current_idx):
    return xml_lines, token_list, current_idx #TODO

def compile_do(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "doStatement", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write do
    token_list, current_idx, xml_lines = compile_subroutineCall(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write ;
    write_partial_token(xml_lines, name = "doStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_return(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "returnStatement", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write return
    if token_list[current_idx+1] != ";":
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
    write_partial_token(xml_lines, name = "returnStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_Statements(token_list, current_idx, xml_lines):
    if token_list[current_idx+2] not in ["let", "if", "while", "do", "return", "else"]:
        return token_list, current_idx, xml_lines
    else:
        if token_list[current_idx] == "let":
            token_list, current_idx, xml_lines = compile_let(token_list, current_idx, xml_lines)
        if token_list[current_idx] == "if":
            token_list, current_idx, xml_lines = compile_ifwhile(token_list, current_idx, xml_lines, name = "if")
        if token_list[current_idx] == "while":
            token_list, current_idx, xml_lines = compile_ifwhile(token_list, current_idx, xml_lines, name = "while")
        if token_list[current_idx] == "do":
            token_list, current_idx, xml_lines = compile_do(token_list, current_idx, xml_lines)
        if token_list[current_idx] == "return":
            token_list, current_idx, xml_lines = compile_return(token_list, current_idx, xml_lines)
        compile_Statements(token_list, current_idx, xml_lines)
        

def compile_subroutineBody(token_list, current_idx, xml_lines):
    token_list, current_idx, xml_lines = compile_varDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_subroutineDec(token_list, current_idx):
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineDec", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write constructor, function, method
    
    if token_list[current_idx] == "void":
        xml_lines, current_idx = write_token(xml_lines, token_list, current_idx)
    elif token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = compile_type(token_list, current_idx, xml_lines)
    
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write subroutine name
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write (
    
    if token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = compile_parameterList(token_list, current_idx, xml_lines)
    else:
        xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterlist", position="beginning")
        xml_lines, current_idx = write_partial_token(xml_lines, name = "parameterList", position="end")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # )
    
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write {  
    token_list, current_idx, xml_lines = compile_subroutineBody(token_list, current_idx, xml_lines) 
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write }
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
    xml_lines, current_idx = write_partial_token(xml_lines, name = "subroutineDec", position="end")
    return token_list, current_idx, xml_lines

def compile_class(token_list, current_idx):
    xml_lines = ["<tokens>"]
    xml_lines, current_idx = write_partial_token(xml_lines, name = "class", position="beginning")
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write class
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write className
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write {
    token_list, current_idx, xml_lines = compile_classVarDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_subroutineDec(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(xml_lines, token_list, current_idx) # write }
    xml_lines, current_idx = write_partial_token(xml_lines, name = "class", position="end")
    return xml_lines.append("</tokens>")