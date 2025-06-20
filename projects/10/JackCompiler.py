symbols = ["}", "{", "[", "(", ".", ",", ";", "]", ")","+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
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
    print(current_idx+1)
    return current_idx+1

def write_token(token_list, current_idx, xml_lines):
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

def compile_varName(token_list, current_idx, xml_lines, use_compile_type = None):
    if use_compile_type:
        token_list, current_idx, xml_lines = write_token(token_list, current_idx, xml_lines)

    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName
    if token_list[current_idx] in [")",";"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write semicolon
        return token_list, current_idx, xml_lines
    elif token_list[current_idx] == ",":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write comma
        return compile_varName(token_list, current_idx, xml_lines, use_compile_type = use_compile_type) #TODO

def compile_classVarDec(token_list, current_idx, xml_lines):
    if token_list[current_idx+1] in ["constructor", "function", "method"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write static | field
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="end")
        return compile_classVarDec(token_list, current_idx, xml_lines)

def compile_varDec(token_list, current_idx, xml_lines):
    if token_list[current_idx+1] in ["let", "if", "while", "do", "return"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines = write_partial_token(xml_lines, name = "VarDec", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write var
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines = write_partial_token(xml_lines, name = "VarDec", position="end")
        return compile_varDec(token_list, current_idx, xml_lines)

def compile_parameterList(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="beginning")
    token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = True)
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
    return token_list, current_idx, xml_lines

def express_compile(xml_lines, token_list, current_idx):
    if token_list[current_idx+1] not in symbols[9:]:
        return xml_lines, token_list, current_idx
    else:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write first thing
        if token_list[current_idx] in [")", "]"]:
            return xml_lines, token_list, current_idx
        elif token_list[current_idx] == "[": # varName[expression]
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write [
            xml_lines, token_list, current_idx = compile_expression(xml_lines, token_list, current_idx)
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ]
        elif token_list[current_idx-1] in ["~", "-"]: # unary op term
            xml_lines, token_list, current_idx = compile_expression(xml_lines, token_list, current_idx)
        elif token_list[current_idx+1] not in symbols[9:]: # (expression)
            xml_lines, token_list, current_idx = compile_expression(xml_lines, token_list, current_idx)
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
        else:
            xml_lines, token_list, current_idx = compile_subroutineCall(xml_lines, token_list, current_idx)
        return express_compile(xml_lines, token_list, current_idx)

def compile_expressionList(xml_lines, token_list, current_idx):
    xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
    token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines, use_compile_type = True)
    xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
    return xml_lines, token_list, current_idx
            
def compile_subroutineCall(xml_lines, token_list, current_idx):
    if token_list[current_idx+1] == "(":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        xml_lines = write_partial_token(xml_lines, name = "Expression", position="beginning")
        if token_list[current_idx+1] == ";":
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
        else:
            xml_lines, current_idx = compile_expressionList(xml_lines, token_list, current_idx)
        xml_lines = write_partial_token(xml_lines, name = "Expression", position="end")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    else:
        for i in range(0,6):
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (,className or varName, ., subroutineName, (
        
        if token_list[current_idx+1] == ";":
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
        else:
            xml_lines, current_idx = compile_expressionList(xml_lines, token_list, current_idx)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )        
    return xml_lines, token_list, current_idx

def compile_expression(xml_lines, token_list, current_idx):
    xml_lines = write_partial_token(xml_lines, name = "Expression", position="beginning")
    xml_lines, token_list, current_idx = express_compile(xml_lines, token_list, current_idx)
    xml_lines = write_partial_token(xml_lines, name = "Expression", position="end")
    return xml_lines, token_list, current_idx 

def compile_let(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "letStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write let
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName   
    if token_list[current_idx] == "[":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write [
        xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ]
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write =   
    xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ;
    write_partial_token(xml_lines, name = "letStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_ifwhile(token_list, current_idx, xml_lines, name = ""):
    write_partial_token(xml_lines, name = f"{name}Statement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
    xml_lines, current_idx = compile_expression(xml_lines, token_list, current_idx)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    if token_list[current_idx] == "else":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write else
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
        token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    write_partial_token(xml_lines, name = f"{name}Statement", position="end")
    return token_list, current_idx, xml_lines

def compile_do(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "doStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write do
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutineName
    token_list, current_idx, xml_lines = compile_subroutineCall(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ;
    write_partial_token(xml_lines, name = "doStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_return(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "returnStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write return
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
        return compile_Statements(token_list, current_idx, xml_lines)

def compile_subroutineBody(token_list, current_idx, xml_lines):
    token_list, current_idx, xml_lines = compile_varDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_subroutineDec(token_list, current_idx):
    xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write constructor, function, method
    
    if token_list[current_idx] == "void":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines)
    elif token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = write_token(token_list, current_idx, xml_lines)
    
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutine name
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
    
    if token_list[current_idx] in ["int", "char", "boolean"]:
        token_list, current_idx, xml_lines = compile_parameterList(token_list, current_idx, xml_lines)
    else:
        xml_lines = write_partial_token(xml_lines, name = "parameterlist", position="beginning")
        xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # )
    
    xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {  
    token_list, current_idx, xml_lines = compile_subroutineBody(token_list, current_idx, xml_lines) 
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
    xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="end")
    return token_list, current_idx, xml_lines

def compile_class(token_list, current_idx):
    xml_lines = ["<tokens>"]
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write class
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write className
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
    token_list, current_idx, xml_lines = compile_classVarDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_subroutineDec(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    return xml_lines.append("</tokens>")