symbols = ["}", "{", "[", "(", ".", ",", ";", "]", ")","+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
integer_constants = list(range(0,32767))

def return_token_type(token):
    if token in symbols:
        token_type = "symbol"
    elif token in keywords:
        token_type = "keyword"
    elif token.isdigit():
        token_type = "integerConstant"
    elif " " in token:
        token_type = "stringConstant"
    else:
        token_type = "identifier"
    return token_type

def advance(current_idx):
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
    else:
        exit(f"Invalid position {position}")
    return xml_lines

def compile_varName(token_list, current_idx, xml_lines, use_compile_type = None):
    if use_compile_type:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines)

    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName
    if token_list[current_idx] in [";"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write semicolon
        return token_list, current_idx, xml_lines
    elif token_list[current_idx] in [")"]:
        return token_list, current_idx, xml_lines
    elif token_list[current_idx] == ",":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write comma
        return compile_varName(token_list, current_idx, xml_lines, use_compile_type = use_compile_type)

def compile_classVarDec(token_list, current_idx, xml_lines):
    if token_list[current_idx] in ["constructor", "function", "method"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write static | field
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="end")
        return compile_classVarDec(token_list, current_idx, xml_lines)

def compile_varDec(token_list, current_idx, xml_lines):
    if token_list[current_idx] in ["let", "if", "while", "do", "return"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines = write_partial_token(xml_lines, name = "varDec", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write var
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = False)
        xml_lines = write_partial_token(xml_lines, name = "varDec", position="end")
        return compile_varDec(token_list, current_idx, xml_lines)

def compile_parameterList(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="beginning")
    token_list, current_idx, xml_lines = compile_varName(token_list, current_idx, xml_lines, use_compile_type = True)
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    return token_list, current_idx, xml_lines

def compile_term(token_list, current_idx, xml_lines):
    #try:
    if token_list[current_idx] == "(":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    elif token_list[current_idx] in ["~", "-"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write op
        token_list, current_idx, xml_lines = compile_term(token_list, current_idx, xml_lines)
    elif token_list[current_idx +1] == "[":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutine- or varname     
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write  (/]     
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write  )/]
    elif token_list[current_idx +1] == "(":
        token_list, current_idx, xml_lines = compile_subroutineCall(token_list, current_idx, xml_lines)
    elif token_list[current_idx +1] == ".":
        token_list, current_idx, xml_lines = compile_subroutineCall(token_list, current_idx, xml_lines)
    else:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varname/integerconstant/stringconstant/keyboardconstant
    # except:
    #     breakpoint()
    return token_list, current_idx, xml_lines

def compile_expressionList(token_list, current_idx, xml_lines):
    if token_list[current_idx] == ")":
        return token_list, current_idx, xml_lines
    else:
        if token_list[current_idx] == ",":
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write comma
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
        return compile_expressionList(token_list, current_idx, xml_lines)

def compile_expression(token_list, current_idx, xml_lines):
    if token_list[current_idx-1] not in ["+", "-", "<", "&", ">"]:
        xml_lines = write_partial_token(xml_lines, name = "expression", position="beginning")
    xml_lines = write_partial_token(xml_lines, name = "term", position="beginning")
    token_list, current_idx, xml_lines = compile_term(token_list, current_idx, xml_lines)
    xml_lines = write_partial_token(xml_lines, name = "term", position="end")

    if token_list[current_idx] in symbols[9:]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write operator
        return compile_expression(token_list, current_idx, xml_lines)       
    else:
        xml_lines = write_partial_token(xml_lines, name = "expression", position="end")
        return token_list, current_idx, xml_lines

        
def compile_subroutineCall(token_list, current_idx, xml_lines):
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write name
    if token_list[current_idx] == "(":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        if token_list[current_idx] == ")":
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
            # xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
        else:
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            token_list, current_idx, xml_lines = compile_expressionList(token_list, current_idx, xml_lines)
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")

        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    else:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write .
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutineName
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        if token_list[current_idx] == ")":
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
            # xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
        else:
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="beginning")
            token_list, current_idx, xml_lines = compile_expressionList(token_list, current_idx, xml_lines)
            xml_lines = write_partial_token(xml_lines, name = "expressionList", position="end")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    return token_list, current_idx, xml_lines

def compile_let(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "letStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write let
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName   
    if token_list[current_idx] == "[":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write [
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ]
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write =   
    token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ;
    xml_lines = write_partial_token(xml_lines, name = "letStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_ifwhile(token_list, current_idx, xml_lines, name = ""):
    xml_lines = write_partial_token(xml_lines, name = f"{name}Statement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write if
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
    token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    if token_list[current_idx] == "else":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write else
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
        token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    xml_lines = write_partial_token(xml_lines, name = f"{name}Statement", position="end")
    return token_list, current_idx, xml_lines

def compile_do(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "doStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write do
    #xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutineName
    token_list, current_idx, xml_lines = compile_subroutineCall(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ;
    xml_lines = write_partial_token(xml_lines, name = "doStatement", position="end")
    return token_list, current_idx, xml_lines

def compile_return(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "returnStatement", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write return
    if token_list[current_idx] != ";":
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write ;
    xml_lines = write_partial_token(xml_lines, name = "returnStatement", position="end")
    return token_list, current_idx, xml_lines


def compile_Statement(token_list, current_idx, xml_lines):
    if token_list[current_idx] not in ["let", "if", "while", "do", "return", "else"]:
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
        return compile_Statement(token_list, current_idx, xml_lines)

def compile_Statements(token_list, current_idx, xml_lines):
    xml_lines = write_partial_token(xml_lines, name = "statements", position="beginning")
    token_list, current_idx, xml_lines = compile_Statement(token_list, current_idx, xml_lines)
    xml_lines = write_partial_token(xml_lines, name = "statements", position="end")
    return token_list, current_idx, xml_lines

def compile_subroutineBody(token_list, current_idx, xml_lines):
    token_list, current_idx, xml_lines = compile_varDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_Statements(token_list, current_idx, xml_lines)
    return token_list, current_idx, xml_lines

def compile_subroutineDec(token_list, current_idx, xml_lines):
    if token_list[current_idx] not in ["constructor", "function", "method"]:
        return token_list, current_idx, xml_lines
    else:
        xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write constructor, function, method
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write void or type
        
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutine name
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        if token_list[current_idx] != ")":
            token_list, current_idx, xml_lines = compile_parameterList(token_list, current_idx, xml_lines)
        else:
            xml_lines = write_partial_token(xml_lines, name = "parameterList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # )
        
        xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {  
        token_list, current_idx, xml_lines = compile_subroutineBody(token_list, current_idx, xml_lines) 
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
        xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="end")
        xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="end")
        return compile_subroutineDec(token_list, current_idx, xml_lines)

def compile_class(token_list, xml_lines, current_idx):
    #xml_lines = ["<tokens>\n"]
    xml_lines = write_partial_token(xml_lines, name = "class", position="beginning")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write class
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write className
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
    token_list, current_idx, xml_lines = compile_classVarDec(token_list, current_idx, xml_lines)
    token_list, current_idx, xml_lines = compile_subroutineDec(token_list, current_idx, xml_lines)
    #breakpoint()
    token_list, current_idx, xml_lines = compile_subroutineDec(token_list, current_idx, xml_lines)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    xml_lines = write_partial_token(xml_lines, name = "class", position="end")
    #xml_lines.append("</tokens>")
    return xml_lines