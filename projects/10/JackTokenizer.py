import re

def contains(thing, member_list):
    if thing in member_list: #TODO
        return true
    return false

def basic_tokenize(lines):
    """Split tokens by whitespace and remove any superfluous whitespace."""
    long_string = " ".join(lines)
    long_string = re.sub(r" {2,}|\n", "", long_string)
    tokens = long_string.split(" ")
    tokens = [token for token in tokens if token]
    print(tokens)
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
    return final_destination