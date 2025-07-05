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

class Tracker: 
    def __init__(self, token_list):
        self.index = 0
        self.tokenList = token_list

    def advance(self, index = None):
        if index:
            self.index += index
        else:
            self.index += 1
    
    def get_token(self):
        return self.tokenList[self.index]

    def prev_token(self, index=None):
        if index:
            return self.tokenList[self.index-index] 
        else:
            return self.tokenList[self.index-1]
        
    def foll_token(self, index=None):
        if index:
            return self.tokenList[self.index-index] 
        else:
            return self.tokenList[self.index-1]


class Symbol:
    def __init__(self, name, kind, type_, n):
        self.name = name
        self.kind = kind
        self.type = type_
        self.n = n

class SymbolTable:
    def __init__(self):
        self.symbols = []

    def new(self, symbol):
        self.symbols = self.symbols.append(symbol)

    def clear(self):
        self.symbols = []


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


def write_partial_token(xml, name = None, position=None):
    if position == "beginning":
        xml.append(f"beginning {name}\n")
    elif position == "end":
        xml.append(f"end {name}\n")
    else:
        exit(f"Invalid position {position}")
    return xml


def compile_varName(token_list,  xml, subroutine_symbols, use_compile_type = None):
    if use_compile_type:
        subroutine_symbols["type"].append(tracker.get_token())
        tracker.advance()
        subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[tracker.get_token()])
        subroutine_symbols = write_correct_kind(subroutine_symbols, tracker.get_token())

    subroutine_symbols["name"].append(tracker.get_token())
    tracker.advance()# write varName
    if tracker.get_token() in [";"]:
        tracker.advance()# write semicolon
        return token_list,  xml, subroutine_symbols
    elif tracker.get_token() in [")"]:
        return token_list,  xml, subroutine_symbols
    elif tracker.get_token() == ",":
        tracker.advance() # write comma
        return compile_varName(token_list,  xml, subroutine_symbols=subroutine_symbols, use_compile_type = use_compile_type)
    
def compile_varName_classVarDec(token_list, xml, global_symbols):
    global_symbols["name"].append(tracker.get_token())
    tracker.advance() # write varName
    if tracker.get_token() in [";"]:
        tracker.advance() # write semicolon
        return token_list, xml, global_symbols
    elif tracker.get_token() in [")"]:
        return token_list, xml, global_symbols
    elif tracker.get_token() == ",":
        tracker.advance() # write comma
        return compile_varName_classVarDec(token_list, xml, global_symbols=global_symbols)


def compile_classVarDec(token_list, xml, global_symbols):
    if tracker.get_token() in ["constructor", "function", "method"]:
        return token_list, xml, global_symbols
    else:
        xml = write_partial_token(xml, name = "classVarDec", position="beginning")
        translated_kind = translate_kind(tracker.get_token())
        global_symbols["number"].append(Counter(global_symbols["kind"])[translated_kind])
        global_symbols= write_correct_kind(global_symbols, tracker.get_token())
        tracker.advance() # write static | field
        global_symbols["type"].append(tracker.get_token())
        tracker.advance() # write type
        token_list, xml, global_symbols = compile_varName_classVarDec(token_list, xml, global_symbols)
        xml = write_partial_token(xml, name = "classVarDec", position="end")
        
        if len(global_symbols["number"]) != len(global_symbols["name"]):
            n_missing = len(global_symbols["name"]) - len(global_symbols["kind"])
            for n in range(0,n_missing):
                global_symbols["number"].append(Counter(global_symbols["kind"])[global_symbols["kind"][-1]])
                global_symbols=write_correct_kind(global_symbols, global_symbols["kind"][-1])
                global_symbols["type"].append(global_symbols["type"][-1])
        return compile_classVarDec(token_list, xml, global_symbols=global_symbols)

def compile_varDec(token_list, xml, subroutine_symbols):
    if tracker.get_token() in ["let", "if", "while", "do", "return"]:
        return token_list, xml, subroutine_symbols
    else:
        xml = write_partial_token(xml, name = "varDec", position="beginning")

        subroutine_symbols = write_correct_kind(subroutine_symbols, tracker.get_token())
        tracker.advance() # write var
        subroutine_symbols["type"].append(tracker.get_token())
        tracker.advance() # write type
        
        token_list, xml, subroutine_symbols = compile_varName(token_list, xml, subroutine_symbols=subroutine_symbols, use_compile_type = False)
        
        if len(subroutine_symbols["type"]) != len(subroutine_symbols["name"]): # Must check against kind or type, not number.
            n_missing =  len(subroutine_symbols["name"]) - len(subroutine_symbols["type"])
            for n in range(0,n_missing):
                subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[subroutine_symbols["kind"][-1]])
                subroutine_symbols=write_correct_kind(subroutine_symbols, subroutine_symbols["kind"][-1])
                subroutine_symbols["type"].append(subroutine_symbols["type"][-1])
        else:
            subroutine_symbols["number"].append(Counter(subroutine_symbols["kind"])[subroutine_symbols["kind"][-1]]-1)
        xml = write_partial_token(xml, name = "varDec", position="end")
        return compile_varDec(token_list, xml, subroutine_symbols=subroutine_symbols)

def compile_parameterList(token_list, xml, subroutine_symbols):
    xml = write_partial_token(xml, name = "parameterList", position="beginning")
    token_list, xml, subroutine_symbols = compile_varName(token_list, xml, subroutine_symbols=subroutine_symbols, use_compile_type = True)
    xml = write_partial_token(xml, name = "parameterList", position="end")
    tracker.advance() # write )
    return token_list, xml, subroutine_symbols

def compile_term(token_list, xml):
    if tracker.get_token() == "(":
        tracker.advance() # write (
        token_list, xml = compile_expression(token_list, xml)
        tracker.advance() # write )
    elif tracker.get_token() in ["~", "-"]:
        tracker.advance() # write op
        xml = write_partial_token(xml, name = "term", position="beginning")
        token_list, xml = compile_term(token_list, xml)
        xml = write_partial_token(xml, name = "term", position="end")
    elif token_list[tracker.index +1] == "[":
        tracker.advance(2) # write subroutine- or varname, write  (/]         
        token_list, xml = compile_expression(token_list, xml)
        tracker.advance() # write  )/]
    elif token_list[tracker.index +1] == "(":
        token_list, xml = compile_subroutineCall(token_list, xml)
    elif token_list[tracker.index +1] == ".":
        token_list, xml = compile_subroutineCall(token_list, xml)
    else:
        tracker.advance() # write varname/integerconstant/stringconstant/keyboardconstant
    return token_list, xml

def compile_expressionList(token_list, xml):
    if tracker.get_token() == ")":
        return token_list, xml
    else:
        if tracker.get_token() == ",":
            tracker.advance() # write comma
        token_list, xml = compile_expression(token_list, xml)
        return compile_expressionList(token_list, xml)

def compile_expression(token_list, xml):
    if token_list[tracker.index-3] in ["let", "1"]:
        xml = write_partial_token(xml, name = "expression", position="beginning")
    elif token_list[tracker.index-1] not in ["+", "-", "<", "&", ">", "*", "/", "|", "="]:
        xml = write_partial_token(xml, name = "expression", position="beginning")
    #elif token_list[current_idx-1] 
    xml = write_partial_token(xml, name = "term", position="beginning")
    token_list, xml = compile_term(token_list, xml)
    xml = write_partial_token(xml, name = "term", position="end")

    if tracker.get_token() in symbols[9:]:
        tracker.advance() # write operator
        return compile_expression(token_list, xml)       
    else:
        xml = write_partial_token(xml, name = "expression", position="end")
        return token_list, xml

        
def compile_subroutineCall(token_list, xml):
    tracker.advance() # write name
    if tracker.get_token() == "(":
        tracker.advance() # write (
        if tracker.get_token() == ")":
            xml = write_partial_token(xml, name = "expressionList", position="beginning")
            xml = write_partial_token(xml, name = "expressionList", position="end")
            # tracker.advance() # write )
        else:
            xml = write_partial_token(xml, name = "expressionList", position="beginning")
            token_list, xml = compile_expressionList(token_list, xml)
            xml = write_partial_token(xml, name = "expressionList", position="end")

        tracker.advance() # write )
    else:
        tracker.advance(3) # write ., subroutineName, (
        if tracker.get_token() == ")":
            xml = write_partial_token(xml, name = "expressionList", position="beginning")
            xml = write_partial_token(xml, name = "expressionList", position="end")
        else:
            xml = write_partial_token(xml, name = "expressionList", position="beginning")
            token_list, xml = compile_expressionList(token_list, xml)
            xml = write_partial_token(xml, name = "expressionList", position="end")
        tracker.advance() # write )
    return token_list, xml

def compile_let(token_list, xml):
    xml = write_partial_token(xml, name = "letStatement", position="beginning")
    tracker.advance(2) # write let, varName
    if tracker.get_token() == "[":
        tracker.advance() # write [
        token_list, xml = compile_expression(token_list, xml)
        tracker.advance() # write ]
    tracker.advance() # write =   
    token_list, xml = compile_expression(token_list, xml)
    tracker.advance() # write ;
    xml = write_partial_token(xml, name = "letStatement", position="end")
    return token_list, xml

def compile_ifwhile(token_list, xml, name = ""):
    xml = write_partial_token(xml, name = f"{name}Statement", position="beginning")
    tracker.advance(2) # write if, (
    token_list, xml = compile_expression(token_list, xml)
    tracker.advance() # write ), {
    _, token_list, xml = compile_Statements(token_list, xml)
    tracker.advance() # write }
    if tracker.get_token() == "else":
        tracker.advance() # write else, {
        _, token_list, xml = compile_Statements(token_list, xml)
        tracker.advance() # write }
    xml = write_partial_token(xml, name = f"{name}Statement", position="end")
    return token_list, xml

def compile_do(token_list, xml):
    xml = write_partial_token(xml, name = "doStatement", position="beginning")
    tracker.advance() # write do
    token_list, xml = compile_subroutineCall(token_list, xml)
    tracker.advance() # write ;
    xml = write_partial_token(xml, name = "doStatement", position="end")
    return token_list, xml

def compile_return(token_list, xml):
    xml = write_partial_token(xml, name = "returnStatement", position="beginning")
    tracker.advance() # write return
    if tracker.get_token() != ";":
        token_list, xml = compile_expression(token_list, xml)
    tracker.advance() # write ;
    xml = write_partial_token(xml, name = "returnStatement", position="end")
    return token_list, xml


def compile_Statement(let_counter, token_list, xml):
    if tracker.get_token() not in ["let", "if", "while", "do", "return", "else"]:
        return let_counter, token_list, xml
    else:
        if tracker.get_token() == "let":
            let_counter += 1
            token_list, xml = compile_let(token_list, xml)
        if tracker.get_token() == "if":
            token_list, xml = compile_ifwhile(token_list, xml, name = "if")
        if tracker.get_token() == "while":
            token_list, xml = compile_ifwhile(token_list, xml, name = "while")
        if tracker.get_token() == "do":
            token_list, xml = compile_do(token_list, xml)
        if tracker.get_token() == "return":
            token_list, xml = compile_return(token_list, xml)
        return compile_Statement(let_counter, token_list, xml)

def compile_Statements(token_list, xml):
    let_counter = 0
    xml = write_partial_token(xml, name = "statements", position="beginning")
    let_counter, token_list, xml = compile_Statement(let_counter, token_list, xml)
    xml = write_partial_token(xml, name = "statements", position="end")
    return let_counter, token_list, xml

def compile_subroutineBody(token_list, xml, subroutine_symbols):
    # Add class name to subroutine symbol table.
    subroutine_symbols["name"].append("this")
    subroutine_symbols["type"].append(token_list[1])
    subroutine_symbols["kind"].append("argument")
    subroutine_symbols["number"].append(0)

    token_list, xml, subroutine_symbols = compile_varDec(token_list, xml, subroutine_symbols)
    let_counter, token_list, xml = compile_Statements(token_list, xml)
    return let_counter, token_list, xml, subroutine_symbols

def compile_subroutineDec(vm_code, token_list, xml, subroutine_symbols):
    if tracker.get_token() not in ["constructor", "function", "method"]:
        return vm_code, token_list, xml, subroutine_symbols
    else:
        xml = write_partial_token(xml, name = "subroutineDec", position="beginning")

        is_constructor = False
        if tracker.get_token() == "constructor":
            is_constructor == True

        tracker.advance(2) # write constructor|function|method, void|type
        
        subroutineName = tracker.get_token()
        tracker.advance(2) # write subroutineName, (
        
        if tracker.get_token() != ")":
            # Add class name to subroutine symbol table.
            subroutine_symbols["name"].append("this")
            subroutine_symbols["type"].append(token_list[1])
            subroutine_symbols["kind"].append("argument")
            subroutine_symbols["number"].append(0)

            token_list, xml, subroutine_symbols = compile_parameterList(token_list, xml, subroutine_symbols=subroutine_symbols)

        else:
            #TODO: mayhaps include something in the subroutine symbol table hier
            xml = write_partial_token(xml, name = "parameterList", position="beginning")
            xml = write_partial_token(xml, name = "parameterList", position="end")
            tracker.advance() # )
        
        vm_code.append(VMWriter.write_functionCall(f"{token_list[1]}.{subroutineName}", len(subroutine_symbols["name"])))
        
        xml = write_partial_token(xml, name = "subroutineBody", position="beginning")
        tracker.advance() # write {  
        let_counter, token_list, xml, subroutine_symbols = compile_subroutineBody(token_list, xml, subroutine_symbols) 
        if is_constructor:
            vm_code.append(VMWriter.write_push("constant", let_counter))   
            vm_code.append(VMWriter.write_misc("call", "Memory.alloc", "1"))     
            vm_code.append(VMWriter.write_pop("pointer", 0))

        tracker.advance() # write }
        xml = write_partial_token(xml, name = "subroutineBody", position="end")
        xml = write_partial_token(xml, name = "subroutineDec", position="end")
        subroutine_symbols = {"name": [], "type": [], "kind": [], "number": []}
        return compile_subroutineDec(vm_code, token_list, xml, subroutine_symbols=subroutine_symbols)

def compile_class(token_list, xml, global_symbols, subroutine_symbols):
    vm_code = []
    global tracker
    tracker = Tracker(token_list)
    tracker.advance(3) # write class, className, {
    token_list, xml, global_symbols = compile_classVarDec(token_list, xml, global_symbols)
    vm_code, token_list, xml, subroutine_symbols = compile_subroutineDec(vm_code, token_list, xml, subroutine_symbols=subroutine_symbols)
    vm_code, token_list, xml, subroutine_symbols = compile_subroutineDec(vm_code, token_list, xml, subroutine_symbols=subroutine_symbols)
    tracker.advance() # write }
    print(vm_code)
    return vm_code, xml

