from collections import Counter

import VMWriter
import utils
from utils import keywords, symbols

integer_constants = list(range(0, 32767))
declarations = {
    "class": 0,
    "static": 0,
    "field": 0,
    "constructor": 0,
    "function": 0,
    "method": 0,
    "var": 0,
}
# subroutine_symbols = {"name": [], "type": [], "kind": [], "number": []}
# global_symbols = {"name": [], "type": [], "kind": [], "number": []}


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


def write_partial_token(xml, name=None, position=None):
    if position == "beginning":
        xml.append(f"beginning {name}\n")
    elif position == "end":
        xml.append(f"end {name}\n")
    else:
        exit(f"Invalid position {position}")
    return xml


def compile_varName(tracker, xml, subroutine_symbols, use_compile_type=None):
    if use_compile_type:
        subroutine_symbols.add_type(tracker.get_token())
        tracker.advance()
        subroutine_symbols.add_kind(translate_kind(tracker.get_token()))

    subroutine_symbols.add_name(tracker.get_token())
    tracker.advance()  # write varName
    if tracker.get_token() in [";"]:
        tracker.advance()  # write semicolon
        return tracker, xml, subroutine_symbols
    elif tracker.get_token() in [")"]:
        return tracker, xml, subroutine_symbols
    elif tracker.get_token() == ",":
        tracker.advance()  # write comma
        return compile_varName(
            tracker,
            xml,
            subroutine_symbols=subroutine_symbols,
            use_compile_type=use_compile_type,
        )


def compile_varName_classVarDec(tracker, xml, global_symbols):
    global_symbols.add_name(tracker.get_token())
    tracker.advance()  # write varName
    if tracker.get_token() in [";"]:
        tracker.advance()  # write semicolon
        return tracker, xml, global_symbols
    elif tracker.get_token() in [")"]:
        return tracker, xml, global_symbols
    elif tracker.get_token() == ",":
        tracker.advance()  # write comma
        return compile_varName_classVarDec(tracker, xml, global_symbols=global_symbols)


def compile_classVarDec(tracker, xml, global_symbols):
    if tracker.get_token() in ["constructor", "function", "method"]:
        return tracker, xml, global_symbols
    else:
        xml = write_partial_token(xml, name="classVarDec", position="beginning")
        translated_kind = translate_kind(tracker.get_token())
        global_symbols.add_kind(translated_kind)
        tracker.advance()  # write static | field
        global_symbols.add_type(tracker.get_token())
        tracker.advance()  # write type
        tracker, xml, global_symbols = compile_varName_classVarDec(
            tracker, xml, global_symbols
        )
        xml = write_partial_token(xml, name="classVarDec", position="end")

        if len(global_symbols.numbers) != len(global_symbols.names):
            n_missing = len(global_symbols.names) - len(global_symbols.kinds)
            for n in range(0, n_missing):
                global_symbols.add_kind(translated_kind(global_symbols.kinds[-1]))
                global_symbols.add_type(global_symbols.types[-1])
        return compile_classVarDec(tracker, xml, global_symbols=global_symbols)


def compile_varDec(tracker, xml, subroutine_symbols):
    if tracker.get_token() in ["let", "if", "while", "do", "return"]:
        return tracker, xml, subroutine_symbols
    else:
        xml = write_partial_token(xml, name="varDec", position="beginning")

        subroutine_symbols.add_kind(translate_kind(tracker.get_token()))
        tracker.advance()  # write var
        subroutine_symbols.add_type(tracker.get_token())
        tracker.advance()  # write type

        tracker, xml, subroutine_symbols = compile_varName(
            tracker, xml, subroutine_symbols=subroutine_symbols, use_compile_type=False
        )

        if len(subroutine_symbols.types) != len(
            subroutine_symbols.names
        ):  # Must check against kind or type, not number.
            n_missing = len(subroutine_symbols.names) - len(subroutine_symbols.types)
            for n in range(0, n_missing):
                subroutine_symbols.add_kind(
                    translate_kind(subroutine_symbols.kinds[-1])
                )
                subroutine_symbols.add_type(subroutine_symbols.types[-1])
        else:
            subroutine_symbols.add_number(subroutine_symbols.kinds[-1])
        xml = write_partial_token(xml, name="varDec", position="end")
        return compile_varDec(tracker, xml, subroutine_symbols=subroutine_symbols)


def compile_parameterList(tracker, xml, subroutine_symbols):
    xml = write_partial_token(xml, name="parameterList", position="beginning")
    tracker, xml, subroutine_symbols = compile_varName(
        tracker, xml, subroutine_symbols=subroutine_symbols, use_compile_type=True
    )
    xml = write_partial_token(xml, name="parameterList", position="end")
    tracker.advance()  # write )
    return tracker, xml, subroutine_symbols


def compile_term(tracker, xml):
    if tracker.get_token() == "(":
        tracker.advance()  # write (
        tracker, xml = compile_expression(tracker, xml)
        tracker.advance()  # write )
    elif tracker.get_token() in ["~", "-"]:
        tracker.advance()  # write op
        xml = write_partial_token(xml, name="term", position="beginning")
        tracker, xml = compile_term(tracker, xml)
        xml = write_partial_token(xml, name="term", position="end")
    elif tracker[tracker.index + 1] == "[":
        tracker.advance(2)  # write subroutine- or varname, write  (/]
        tracker, xml = compile_expression(tracker, xml)
        tracker.advance()  # write  )/]
    elif tracker[tracker.index + 1] == "(":
        tracker, xml = compile_subroutineCall(tracker, xml)
    elif tracker[tracker.index + 1] == ".":
        tracker, xml = compile_subroutineCall(tracker, xml)
    else:
        tracker.advance()  # write varname/integerconstant/stringconstant/keyboardconstant
    return tracker, xml


def compile_expressionList(tracker, xml):
    if tracker.get_token() == ")":
        return tracker, xml
    else:
        if tracker.get_token() == ",":
            tracker.advance()  # write comma
        tracker, xml = compile_expression(tracker, xml)
        return compile_expressionList(tracker, xml)


def compile_expression(tracker, xml):
    if tracker[tracker.index - 3] in ["let", "1"]:
        xml = write_partial_token(xml, name="expression", position="beginning")
    elif tracker[tracker.index - 1] not in ["+", "-", "<", "&", ">", "*", "/", "|", "="]:
        xml = write_partial_token(xml, ncame="expression", position="beginning")
    xml = write_partial_token(xml, name="term", position="beginning")
    tracker, xml = compile_term(tracker, xml)
    xml = write_partial_token(xml, name="term", position="end")

    if tracker.get_token() in symbols[9:]:
        tracker.advance()  # write operator
        return compile_expression(tracker, xml)
    else:
        xml = write_partial_token(xml, name="expression", position="end")
        return tracker, xml


def compile_subroutineCall(tracker, xml):
    tracker.advance()  # write name
    if tracker.get_token() == "(":
        tracker.advance()  # write (
        if tracker.get_token() == ")":
            xml = write_partial_token(xml, name="expressionList", position="beginning")
            xml = write_partial_token(xml, name="expressionList", position="end")
        else:
            xml = write_partial_token(xml, name="expressionList", position="beginning")
            tracker, xml = compile_expressionList(tracker, xml)
            xml = write_partial_token(xml, name="expressionList", position="end")

        tracker.advance()  # write )
    else:
        tracker.advance(3)  # write ., subroutineName, (
        if tracker.get_token() == ")":
            xml = write_partial_token(xml, name="expressionList", position="beginning")
            xml = write_partial_token(xml, name="expressionList", position="end")
        else:
            xml = write_partial_token(xml, name="expressionList", position="beginning")
            tracker, xml = compile_expressionList(tracker, xml)
            xml = write_partial_token(xml, name="expressionList", position="end")
        tracker.advance()  # write )
    return tracker, xml


def compile_let(tracker, xml):
    xml = write_partial_token(xml, name="letStatement", position="beginning")
    tracker.advance(2)  # write let, varName
    if tracker.get_token() == "[":
        tracker.advance()  # write [
        tracker, xml = compile_expression(tracker, xml)
        tracker.advance()  # write ]
    tracker.advance()  # write =
    tracker, xml = compile_expression(tracker, xml)
    tracker.advance()  # write ;
    xml = write_partial_token(xml, name="letStatement", position="end")
    return tracker, xml


def compile_ifwhile(tracker, xml, name=""):
    xml = write_partial_token(xml, name=f"{name}Statement", position="beginning")
    tracker.advance(2)  # write if, (
    tracker, xml = compile_expression(tracker, xml)
    tracker.advance()  # write ), {
    _, tracker, xml = compile_Statements(tracker, xml)
    tracker.advance()  # write }
    if tracker.get_token() == "else":
        tracker.advance()  # write else, {
        _, tracker, xml = compile_Statements(tracker, xml)
        tracker.advance()  # write }
    xml = write_partial_token(xml, name=f"{name}Statement", position="end")
    return tracker, xml


def compile_do(tracker, xml):
    xml = write_partial_token(xml, name="doStatement", position="beginning")
    tracker.advance()  # write do
    tracker, xml = compile_subroutineCall(tracker, xml)
    tracker.advance()  # write ;
    xml = write_partial_token(xml, name="doStatement", position="end")
    return tracker, xml


def compile_return(tracker, xml):
    xml = write_partial_token(xml, name="returnStatement", position="beginning")
    tracker.advance()  # write return
    if tracker.get_token() != ";":
        tracker, xml = compile_expression(tracker, xml)
    tracker.advance()  # write ;
    xml = write_partial_token(xml, name="returnStatement", position="end")
    return tracker, xml


def compile_Statement(let_counter, tracker, xml):
    if tracker.get_token() not in ["let", "if", "while", "do", "return", "else"]:
        return let_counter, tracker, xml
    else:
        if tracker.get_token() == "let":
            let_counter += 1
            tracker, xml = compile_let(tracker, xml)
        if tracker.get_token() == "if":
            tracker, xml = compile_ifwhile(tracker, xml, name="if")
        if tracker.get_token() == "while":
            tracker, xml = compile_ifwhile(tracker, xml, name="while")
        if tracker.get_token() == "do":
            tracker, xml = compile_do(tracker, xml)
        if tracker.get_token() == "return":
            tracker, xml = compile_return(tracker, xml)
        return compile_Statement(let_counter, tracker, xml)


def compile_Statements(tracker, xml):
    let_counter = 0
    xml = write_partial_token(xml, name="statements", position="beginning")
    let_counter, tracker, xml = compile_Statement(let_counter, tracker, xml)
    xml = write_partial_token(xml, name="statements", position="end")
    return let_counter, tracker, xml


def compile_subroutineBody(tracker, xml, subroutine_symbols):
    # Add class name to subroutine symbol table.
    subroutine_symbols.new(name="this", kind="argument", type_=tracker[1])

    tracker, xml, subroutine_symbols = compile_varDec(tracker, xml, subroutine_symbols)
    let_counter, tracker, xml = compile_cStatements(tracker, xml)
    return let_counter, tracker, xml, subroutine_symbols


def compile_subroutineDec(vm_code, tracker, xml, subroutine_symbols):
    if tracker.get_token() not in ["constructor", "function", "method"]:
        return vm_code, tracker, xml, subroutine_symbols
    else:
        xml = write_partial_token(xml, name="subroutineDec", position="beginning")

        is_constructor = False
        if tracker.get_token() == "constructor":
            is_constructor == True

        tracker.advance(2)  # write constructor|function|method, void|type

        subroutineName = tracker.get_token()
        tracker.advance(2)  # write subroutineName, (

        if tracker.get_token() != ")":
            # Add class name to subroutine symbol table.
            subroutine_symbols.new(name="this", kind="argument", type_=tracker[1])

            tracker, xml, subroutine_symbols = compile_parameterList(
                tracker, xml, subroutine_symbols=subroutine_symbols
            )

        else:
            # TODO: mayhaps include something in the subroutine symbol table hier
            xml = write_partial_token(xml, name="parameterList", position="beginning")
            xml = write_partial_token(xml, name="parameterList", position="end")
            tracker.advance()  # )

        vm_code.append(
            VMWriter.write_functionCall(
                f"{tracker[1]}.{subroutineName}", len(subroutine_symbols["name"])
            )
        )

        xml = write_partial_token(xml, name="subroutineBody", position="beginning")
        tracker.advance()  # write {
        let_counter, tracker, xml, subroutine_symbols = compile_subroutineBody(
            tracker, xml, subroutine_symbols
        )
        if is_constructor:
            vm_code.append(VMWriter.write_push("constant", let_counter))
            vm_code.append(VMWriter.write_misc("call", "Memory.alloc", "1"))
            vm_code.append(VMWriter.write_pop("pointer", 0))

        tracker.advance()  # write }
        xml = write_partial_token(xml, name="subroutineBody", position="end")
        xml = write_partial_token(xml, name="subroutineDec", position="end")
        subroutine_symbols.clear()
        return compile_subroutineDec(
            vm_code, tracker, xml, subroutine_symbols=subroutine_symbols
        )


def compile_class(tracker, xml, global_symbols, subroutine_symbols):

    vm_code = []
    tracker.advance(3)  # write class, className, {
    tracker, xml, global_symbols = compile_classVarDec(tracker, xml, global_symbols)
    vm_code, tracker, xml, subroutine_symbols = compile_subroutineDec(
        vm_code, tracker, xml, subroutine_symbols=subroutine_symbols
    )
    vm_code, tracker, xml, subroutine_symbols = compile_subroutineDec(
        vm_code, tracker, xml, subroutine_symbols=subroutine_symbols
    )
    tracker.advance()  # write }
    print(vm_code)
    return vm_code, xml
