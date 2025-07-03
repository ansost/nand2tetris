"""Parser for the Hack language."""

import re
import os
import argparse
from collections import Counter

import JackTokenizer
from JackTokenizer import *

import JackCompiler
from JackCompiler import *


def remove_comments(lines):
    """Removes comments with thy syntax: /** */ or // ."""
    cleaned = []
    for line in lines:
        line = re.sub(r"(//.*?$)|^ \*.*$|/\*\*.*$", "", line)
        line = re.sub(r"\t", "", line)
        if line:
            cleaned.append(line)
    return cleaned


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--source",
        required=False,
        help="File with '.jack' extension or path to folder containing '.jack' files. If nothing is passed, the current directory is used as input.",
        type=str,
    )
    args = parser.parse_args()

    symbols = [
        "}",
        "{",
        "[",
        "]",
        "(",
        ")",
        ".",
        ",",
        ";",
        "+",
        "-",
        "*",
        "/",
        "&",
        "|",
        ">",
        "<",
        "=",
        "~",
    ]
    keywords = [
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return",
    ]
    integer_constants = list(range(0, 32767))

    # Read in files.
    if args.source:
        if ".jack" in args.source:
            path = os.path.dirname(args.source)
            files = [os.path.basename(args.source)]
        else:
            path = os.path.realpath(args.source)
            files = [
                file
                for file in os.listdir(path)
                if os.path.realpath(file).endswith(".jack")
            ]
    else:
        path = os.getcwd()
        files = [
            file
            for file in os.listdir(path)
            if os.path.realpath(file).endswith(".jack")
        ]

    if not files:
        print(f"No files found in {path}!")
        exit()

    for file in files:
        xml_lines = []
        with open(os.path.join(path, file), "r") as f:
            raw_lines = f.readlines()
        lines = remove_comments(raw_lines)
        tokens = detailed_tokenize(lines, symbols)

        # Debugging:
        # with open(file +".tokens", "w") as f:
        #     f.writelines([str(line)+"\n" for line in tokens])

        # Write xml code.
        vm_code, xml_lines = compile_class(tokens, xml_lines, current_idx=0, global_symbols=global_symbols, subroutine_symbols=subroutine_symbols)
        finished_xml_lines = []
        for line in xml_lines:
            line = re.sub(r"> < <", "> &lt; <", line)
            line = re.sub(r"> > <", "> &gt; <", line)
            line = re.sub(r"> & <", "> &amp; <", line)
            finished_xml_lines.append(line)

        print(global_symbols)

        new_filename = file.split(".")[0] + "T.xml"
        with open(os.path.join(path, new_filename), "w") as f:
            f.writelines([line for line in finished_xml_lines])
        print(f"File {file} done!")
