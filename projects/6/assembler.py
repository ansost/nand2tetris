"""Translate an .asm file to binary instructions in ".hack"."""
import os
import re
import json
import argparse


def process_rom_symbols(rom_symbols, unkown_symbol_counter, ram_symbol_lookup, command):
    """Add command if command is not in rom or ram symbols."""
    if command not in ram_symbol_lookup and command not in rom_symbols:
        rom_symbols[command] = unkown_symbol_counter
        unkown_symbol_counter += 1
        rom_address = rom_symbols[command]
    elif command in ram_symbol_lookup:
        rom_address = ram_symbol_lookup[command]
    elif command in rom_symbols:
        rom_address = rom_symbols[command]
    address = return_address(rom_address)
    return address, unkown_symbol_counter


def return_address(command):
    """Return 16 bit binary number from decimal."""
    address = "{0:016b}".format(int(command))
    return address


def encode_computation(computation_lookup, operation):
    """Lookup the computation bits for the given anonymized operation."""
    anonymous_operation = re.sub(r"[AM]", "X", operation)
    encoded_computation = computation_lookup[anonymous_operation]
    return encoded_computation


def build_c_instruction(jump_lookup, destination_lookup, computation_lookup, command):
    """Construct different types of c-intructions from jump-, a-, copmutation- and destination-bits."""
    if ";" in command:
        operation, jmp_condition = command.split(";")
        jmp_bits = jump_lookup[jmp_condition]
        dest_bits = "000"
    else:
        destination, operation = command.split("=")
        dest_bits = destination_lookup[destination]
        jmp_bits = "000"

    if "M" in operation:
        a_bit = "1"
    else:
        a_bit = "0"

    computation = encode_computation(computation_lookup, operation)
    return "111" + a_bit + computation + dest_bits + jmp_bits


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in",
        "--input_file",
        required=True,
        help="The file to be translated from asm to hack. Must include the file ending and its path if the file is not in the current path.",
        type=str,
    )
    args = parser.parse_args()

    # Load dictionaires for jump, destination, computation and symbol bits/addresses.
    with open("lookups.json", "r") as f:
        lookups = json.load(f)

    # Read and commands and remove newlines, line-final spaces and empty lines.
    with open(args.input_file, "r") as f:
        asm_commands = f.readlines()
    asm_commands_stripped = [
        command.strip("\n").strip() for command in asm_commands if not "//" in command
    ]
    asm_commands_stripped = [line for line in asm_commands_stripped if line]

    # Add ROM symbols.
    rom_symbols = {}
    for index, command in enumerate(asm_commands_stripped):
        if "(" in command:
            actual_index = index - len(rom_symbols)
            rom_symbols[re.sub(r"[\(\)]", "", command)] = actual_index

    # Translate asm to hack.
    hack_commands = []
    unkown_symbol_counter = 16
    for command in asm_commands_stripped:
        if "@" in command:
            if command[1].isalpha():
                binary_command, unkown_symbol_counter = process_rom_symbols(
                    rom_symbols, unkown_symbol_counter, lookups["symbols"], command[1:]
                )
            else:
                binary_command = return_address(command[1:])
        elif "=" in command or ";" in command:
            binary_command = build_c_instruction(
                lookups["jumps"],
                lookups["destinations"],
                lookups["computations"],
                command,
            )
        else:  # Ignore pseudocommands.
            continue
        hack_commands.append(binary_command)

    # Save assembled code.
    out_file_name = os.path.basename(args.input_file).split(".")[0] + ".hack"
    out_path = os.path.dirname(args.input_file)
    with open(os.path.join(out_path, out_file_name), "w") as f:
        f.writelines([str(command) + "\n" for command in hack_commands])
