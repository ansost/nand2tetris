import re

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

def basic_tokenize(lines):
    """Split tokens by whitespace and remove any superfluous whitespace."""
    long_string = " ".join(lines)
    long_string = re.sub(r" {2,}|\n", "", long_string)
    tokens = long_string.split(" ")
    tokens = [token for token in tokens if token]
    # print(tokens)
    breakpoint()
    return tokens

def detailed_tokenize(lines, symbols):
    """Split characters from tokens if they are symbols."""
    tokens = basic_tokenize(lines)
    final_destination = []
    for token in tokens:
        subword = []
        for char in token:
            if char in symbols:
                if subword:
                    final_destination.extend(["".join(subword), char])
                    subword = []
                else:
                    final_destination.append(char)
            else:
                subword.append(char)
        if subword:
            final_destination.append("".join(subword))
    breakpoint()
    
    return final_destination