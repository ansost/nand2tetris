from collections import Counter

import VMWriter

symbols = ["}", "{", "[", "(", ".", ",", ";", "]", ")","+", "-", "*", "/", "&", "|", ">", "<", "=", "~"]
keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
integer_constants = list(range(0,32767))
declarations = {"class" : 0,
                "static": 0,
                "field": 0,
                "constructor": 0,
                "function": 0,
                "method" : 0,
                "var": 0}
subroutine_symbols = {"name": [], "type": [], "kind": [], "number": []} 
global_symbols = {"name": [], "type": [], "kind": [], "number": []}

def search_var(global_symbols, subroutine_symbols, var):
    if var in subroutine_symbols["name"]:
        index = subroutine_symbols["name"].index(var)
        segment = subroutine_symbols["kind"][index]
        count = subroutine_symbols["number"][index]
        return (segment, count)
    elif var in global_symbols["name"]:
        index = global_symbols["name"].index(var)
        segment = global_symbols["kind"][index]
        count = global_symbols["number"][index]
        return (segment, count)
    else:
        return False


def translate_kind(kind):
    if kind == "field":
        translated_kind = "this"
    elif kind == "var":
        translated_kind = "local"
    else:
        translated_kind = kind
    return translated_kind

def write_correct_kind(dictionary, kind):
    kind = translate_kind(kind)
    dictionary["kind"].append(kind)
    return dictionary

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
    if token_list[current_idx] in declarations.keys():
        name = return_token_type(token_list[current_idx])
        xml_lines.append(f"{token_list[current_idx]} declaration, number: {declarations[token_list[current_idx]]}\n")
        declarations[token_list[current_idx]] +=1
        current_idx = advance(current_idx)
    else:
        name = return_token_type(token_list[current_idx])
        xml_lines.append(f"{name} {token_list[current_idx]}\n")
        current_idx = advance(current_idx)
    return xml_lines, current_idx

def write_partial_token(xml_lines, name = None, position=None):
    if position == "beginning":
        xml_lines.append(f"beginning {name}\n")
    elif position == "end":
        xml_lines.append(f"end {name}\n")
    else:
        exit(f"Invalid position {position}")
    return xml_lines

def compile_varName(token_list, current_idx, xml_lines, subroutine_symbols, use_compile_type = None):
    if use_compile_type:
        subroutine_symbols["type"].append(token_list[current_idx])
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines)
        subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[token_list[current_idx]])
        subroutine_symbols = write_correct_kind(subroutine_symbols, token_list[current_idx])

    subroutine_symbols["name"].append(token_list[current_idx])
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName
    if token_list[current_idx] in [";"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write semicolon
        return token_list, current_idx, xml_lines, subroutine_symbols
    elif token_list[current_idx] in [")"]:
        return token_list, current_idx, xml_lines, subroutine_symbols
    elif token_list[current_idx] == ",":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write comma
        return compile_varName(token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols, use_compile_type = use_compile_type)
    
def compile_varName_classVarDec(token_list, current_idx, xml_lines, global_symbols):
    global_symbols["name"].append(token_list[current_idx])
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write varName
    if token_list[current_idx] in [";"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write semicolon
        return token_list, current_idx, xml_lines, global_symbols
    elif token_list[current_idx] in [")"]:
        return token_list, current_idx, xml_lines, global_symbols
    elif token_list[current_idx] == ",":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write comma
        return compile_varName_classVarDec(token_list, current_idx, xml_lines, global_symbols=global_symbols)

def compile_classVarDec(token_list, current_idx, xml_lines, global_symbols):
    if token_list[current_idx] in ["constructor", "function", "method"]:
        return token_list, current_idx, xml_lines, global_symbols
    else:
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="beginning")
        translated_kind = translate_kind(token_list[current_idx])
        global_symbols["number"].append(Counter(global_symbols["kind"])[translated_kind])
        global_symbols= write_correct_kind(global_symbols, token_list[current_idx])
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write static | field
        global_symbols["type"].append(token_list[current_idx])
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        token_list, current_idx, xml_lines, global_symbols = compile_varName_classVarDec(token_list, current_idx, xml_lines, global_symbols)
        xml_lines = write_partial_token(xml_lines, name = "classVarDec", position="end")
        
        if len(global_symbols["number"]) != len(global_symbols["name"]):
            n_missing = len(global_symbols["name"]) - len(global_symbols["kind"])
            for n in range(0,n_missing):
                global_symbols["number"].append(Counter(global_symbols["kind"])[global_symbols["kind"][-1]])
                global_symbols=write_correct_kind(global_symbols, global_symbols["kind"][-1])
                global_symbols["type"].append(global_symbols["type"][-1])
        return compile_classVarDec(token_list, current_idx, xml_lines, global_symbols=global_symbols)

def compile_varDec(token_list, current_idx, xml_lines, subroutine_symbols):
    if token_list[current_idx] in ["let", "if", "while", "do", "return"]:
        return token_list, current_idx, xml_lines, subroutine_symbols
    else:
        xml_lines = write_partial_token(xml_lines, name = "varDec", position="beginning")

        subroutine_symbols = write_correct_kind(subroutine_symbols, token_list[current_idx])
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write var
        subroutine_symbols["type"].append(token_list[current_idx])
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write type
        
        token_list, current_idx, xml_lines, subroutine_symbols = compile_varName(token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols, use_compile_type = False)
        
        if len(subroutine_symbols["type"]) != len(subroutine_symbols["name"]): # Must check against kind or type, not number.
            n_missing =  len(subroutine_symbols["name"]) - len(subroutine_symbols["type"])
            for n in range(0,n_missing):
                subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[subroutine_symbols["kind"][-1]])
                subroutine_symbols=write_correct_kind(subroutine_symbols, subroutine_symbols["kind"][-1])
                subroutine_symbols["type"].append(subroutine_symbols["type"][-1])
        else:
            subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[subroutine_symbols["kind"][-1]]-1)
        #breakpoint()
        xml_lines = write_partial_token(xml_lines, name = "varDec", position="end")
        return compile_varDec(token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols)

def compile_parameterList(token_list, current_idx, xml_lines, subroutine_symbols):
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="beginning")
    token_list, current_idx, xml_lines, subroutine_symbols = compile_varName(token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols, use_compile_type = True)
    xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    return token_list, current_idx, xml_lines, subroutine_symbols

def compile_term(token_list, current_idx, xml_lines):
    if token_list[current_idx] == "(":
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        token_list, current_idx, xml_lines = compile_expression(token_list, current_idx, xml_lines)
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write )
    elif token_list[current_idx] in ["~", "-"]:
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write op
        xml_lines = write_partial_token(xml_lines, name = "term", position="beginning")
        token_list, current_idx, xml_lines = compile_term(token_list, current_idx, xml_lines)
        xml_lines = write_partial_token(xml_lines, name = "term", position="end")
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
    if token_list[current_idx-3] in ["let", "1"]:
        xml_lines = write_partial_token(xml_lines, name = "expression", position="beginning")
    elif token_list[current_idx-1] not in ["+", "-", "<", "&", ">", "*", "/", "|", "="]:
        xml_lines = write_partial_token(xml_lines, name = "expression", position="beginning")
    #elif token_list[current_idx-1] 
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


def compile_Statement(let_counter, token_list, current_idx, xml_lines):
    if token_list[current_idx] not in ["let", "if", "while", "do", "return", "else"]:
        return let_counter, token_list, current_idx, xml_lines
    else:
        if token_list[current_idx] == "let":
            let_counter += 1
            token_list, current_idx, xml_lines = compile_let(token_list, current_idx, xml_lines)
        if token_list[current_idx] == "if":
            token_list, current_idx, xml_lines = compile_ifwhile(token_list, current_idx, xml_lines, name = "if")
        if token_list[current_idx] == "while":
            token_list, current_idx, xml_lines = compile_ifwhile(token_list, current_idx, xml_lines, name = "while")
        if token_list[current_idx] == "do":
            token_list, current_idx, xml_lines = compile_do(token_list, current_idx, xml_lines)
        if token_list[current_idx] == "return":
            token_list, current_idx, xml_lines = compile_return(token_list, current_idx, xml_lines)
        return compile_Statement(let_counter, token_list, current_idx, xml_lines)

def compile_Statements(token_list, current_idx, xml_lines):
    let_counter = 0
    xml_lines = write_partial_token(xml_lines, name = "statements", position="beginning")
    let_counter, token_list, current_idx, xml_lines = compile_Statement(let_counter, token_list, current_idx, xml_lines)
    xml_lines = write_partial_token(xml_lines, name = "statements", position="end")
    return let_counter, token_list, current_idx, xml_lines

def compile_subroutineBody(token_list, current_idx, xml_lines, subroutine_symbols):
    # Add class name to subroutine symbol table.
    subroutine_symbols["name"].append("this")
    subroutine_symbols["type"].append(token_list[1])
    subroutine_symbols["kind"].append("argument")
    subroutine_symbols["number"].append(0)

    token_list, current_idx, xml_lines, subroutine_symbols = compile_varDec(token_list, current_idx, xml_lines, subroutine_symbols)
    let_counter, token_list, current_idx, xml_lines = compile_Statements(let_counter, token_list, current_idx, xml_lines)
    return let_counter, token_list, current_idx, xml_lines, subroutine_symbols

def compile_subroutineDec(vm_code, token_list, current_idx, xml_lines, subroutine_symbols):
    if token_list[current_idx] not in ["constructor", "function", "method"]:
        return vm_code, token_list, current_idx, xml_lines, subroutine_symbols
    else:
        xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="beginning")

        is_constructor = False
        if token_list[current_idx] == "constructor":
            is_constructor == True

        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write constructor, function, method
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write void or type
        
        subroutineName = token_list[current_idx]
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write subroutineName
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write (
        
        if token_list[current_idx] != ")":
            # Add class name to subroutine symbol table.
            subroutine_symbols["name"].append("this")
            subroutine_symbols["type"].append(token_list[1])
            subroutine_symbols["kind"].append("argument")
            subroutine_symbols["number"].append(0)

            token_list, current_idx, xml_lines, subroutine_symbols = compile_parameterList(token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols)

        else:
            #TODO: mayhaps include something in the subroutine symbol table hier
            xml_lines = write_partial_token(xml_lines, name = "parameterList", position="beginning")
            xml_lines = write_partial_token(xml_lines, name = "parameterList", position="end")
            xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # )
        
        vm_code.append(VMWriter.write_functionCall(f"{token_list[1]}.{subroutineName}", len(subroutine_symbols["name"])))
        
        xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="beginning")
        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {  
        let_counter, token_list, current_idx, xml_lines, subroutine_symbols = compile_subroutineBody(token_list, current_idx, xml_lines, subroutine_symbols) 
        if is_constructor:
            vm_code.append(VMWriter.write_push("constant", let_counter))   
            vm_code.append(VMWriter.write_misc("call", "Memory.alloc", "1"))     
            vm_code.append(VMWriter.write_pop("pointer", 0))

        xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
        xml_lines = write_partial_token(xml_lines, name = "subroutineBody", position="end")
        xml_lines = write_partial_token(xml_lines, name = "subroutineDec", position="end")
        subroutine_symbols = {"name": [], "type": [], "kind": [], "number": []}
        return compile_subroutineDec(vm_code, token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols)

def compile_class(token_list, xml_lines, current_idx, global_symbols, subroutine_symbols):
    vm_code = []
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write class
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write className
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write {
    token_list, current_idx, xml_lines, global_symbols = compile_classVarDec(token_list, current_idx, xml_lines, global_symbols)
    vm_code, token_list, current_idx, xml_lines, subroutine_symbols = compile_subroutineDec(vm_code, token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols)
    vm_code, token_list, current_idx, xml_lines, subroutine_symbols = compile_subroutineDec(vm_code, token_list, current_idx, xml_lines, subroutine_symbols=subroutine_symbols)
    xml_lines, current_idx = write_token(token_list, current_idx, xml_lines) # write }
    print(vm_code)
    return vm_code, xml_lines