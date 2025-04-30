"""[...]"""
import re
import os
import argparse


def return_adress(decimal_number):
    """[TBD]"""
    address = "{0:016b}".format(decimal_number)
    return address

def encode_dest(destination):
    """Return the corresponding destination bits for the given destination."""
    codes = {
        "null": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }
    return codes[destination]

def select_jump(command):
    """Return the jump bits for the given jump instruction."""
    codes = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }
    return codes[command]

def lookup_comp_bits(operation):
    """Lookup the computation bits for the given operation."""
    anonymous_operation = re.sub(r"[AM]", "X", operation)
    comp_bits = {
        "0":"101010",
        "1":"111111",
        "-1": "111010",
        "D":"001100",
        "X":"110000",
        "!D": "001101",
        "!X": "110001",
        "-D":"001111",
        "-X":"110011",
        "D+1":"011111",
        "X+1":"110111",
        "D-1":"001110",
        "X-1":"110010",
        "D+X":"000010",
        "D-X":"010011",
        "D&X":"000000",
        "D|X":"010101"
    }
    return comp_bits[anonymous_operation]

def select_computation(command):
    destination, operation = command.split("=") 
    dest_bits = encode_dest(destination)

    if "M" in operation:
        a_bit = "1"
    else:
        a_bit = "0"
    
    computation = lookup_comp_bits(operation)
        
    return "111" + a_bit + computation + dest_bits + "000"


def translate_command(command):
    if "@" in command:
        address = return_adress(command[1:])
        return address

    if ";" in command:
        jump = select_jump(command)

    if "=" in command:
        alu_cmd = select_computation(command)
        return alu_cmd


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in",
        "--input_file",
        required=True,
        help="The file to be translated from asm to hack. Must include the file ending and path if the file is not in the current path.",
        type=str,
    )
    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        commands = f.readlines()

    commands_stripped = [
        command.strip("\n") for command in commands if not command.startswith("//")
    ]  # TODO remove empty strings
    breakpoint()
    translated_list = [translate_command(command) for command in commands if command]

    with open(args.infile) as f:
        f.writelines()  # TODO maybe turn into ints
