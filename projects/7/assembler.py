"""Translate an .asm file to binary instructions in ".hack"."""
import os
import json
import argparse

import yaml

def do_push(commands):
    return f"""@{commands[1]}
D=A
@SP
AM=M+1
A=A-1
M=D"""

def do_pop(commands):
    return """@SP
AM=M-1
D=M"""

def update_stack(commands):
    if commands[0] == "push":
        cmd = do_push(commands[1:])
    else:
        cmd = do_pop(commands[1:])
    return cmd

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

    # Read and commands and remove newlines, line-final spaces and empty lines.
    with open(args.input_file, "r") as f:
        vm_commands = f.readlines()
    vm_commands_stripped = [
        command.strip("\n").strip() for command in vm_commands if not "//" in command
    ]
    vm_commands_stripped = [line for line in vm_commands_stripped if line]

    # Load dictionaires for jump, destination, computation and symbol bits/addresses.
    with open("arithmetic_operations.yaml", "r") as f:
        arithmetic_operations = yaml.safe_load(f)

    # Translate.
    asm_commands = []
    for cmd in vm_commands_stripped:
        commands = cmd.split()
        if len(commands) == 1:
            asm = arithmetic_operations[commands[0]]
        else:
            asm = update_stack(commands)
        asm_commands.append(asm)

    # Save assembled code.
    out_file_name = os.path.basename(args.input_file).split(".")[0] + ".asm"
    out_path = os.path.dirname(args.input_file)
    with open(os.path.join(out_path, out_file_name), "w") as f:
        f.writelines([str(command) + "\n" for command in asm_commands])
