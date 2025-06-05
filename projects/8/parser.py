import argparse
import sys
import os
import yaml
from collections import defaultdict
from vm_translator import *

def parse_commands(command):
    if len(command.split()) < 2:
        if command.split()[0] == "return":
            command_type = "return"
        else:
            command_type = "arithmetic"
    else:
        command_type = command.split()[0]
    return command_type


if __name__ == "__main__":
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "-in",
    #     "--input",
    #     required=True,
    #     help="VM file or folder translated to hack language",
    #     type=str,
    # )
    # args = parser.parse_args()
    
    # Unterscheidung path oder file
    init = False
    if os.path.isdir(sys.argv[1]):
        files = [file for file in os.listdir(sys.argv[1])]

    else:
        files = [os.path.basename(sys.argv[1]).split(".")[0]]


    # Read and commands and remove newlines, line-final spaces and empty lines

    with open('lookup.yaml', 'r') as file:
        lookups = yaml.safe_load(file)
    
    files = [file for file in files if file.endswith(".vm")]

    if len(files) > 1:
        init =True

    asm_commands = []
    if init:
        asm_commands.append(write_init())
        asm_commands.insert(1,write_call(lookups,"call Sys.init 0",0)[0])
    for file in files:
        with open(f"{sys.argv[1]}/{file}", 'r') as f:
            vm_commands = f.readlines()

        vm_commands_stripped = [
            command.strip("\n").strip() for command in vm_commands if not command.startswith("//")]
        vm_commands_stripped = [line.split("/")[0].strip() for line in vm_commands_stripped]
        vm_commands_stripped = [line for line in vm_commands_stripped if line]

        cmd_tracker = defaultdict(int)

        for command in vm_commands_stripped:
            function_name = ""  
            command_type = parse_commands(command)
            if command_type == "arithmetic":
                translated_command, cmd_tracker = write_arithmetic(lookups, command, cmd_tracker)
            elif command_type == "push":
                translated_command = write_push_pop(lookups, command, file[:-3])
            elif command_type == "pop":
                translated_command = write_push_pop(lookups, command, file[:-3])
            elif command_type == "label":
                translated_command = write_label(command,function_name)
            elif command_type == "goto":
                translated_command = write_goto(lookups, command, function_name)
            elif command_type == "if-goto":
                translated_command = write_ifgoto(lookups, command, function_name)
            elif command_type == "function":
                function = command.split()[1]
                translated_command, function_name = write_function(lookups, command)
            elif command_type == "return":
                translated_command = write_return(lookups, command)
            elif command_type == "call":
                translated_command, callcount = write_call(lookups,command, callcount)
            asm_commands.append(translated_command)

    # Save translated code.
    out_file_name = os.path.basename(os.path.normpath(sys.argv[1])) + ".asm"
    out_path = os.path.dirname(sys.argv[1])
    with open(os.path.join(out_path, out_file_name), "w") as f:
        f.writelines([str(command) + "\n" for command in asm_commands])