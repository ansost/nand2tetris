import argparse
import os
import yaml
from collections import defaultdict

segments = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT"}
segments2 = {"that":"THAT", "this":"THIS","argument":"ARG","local":"LCL"}
callcount = 0

# write Sys.ini
def write_init():
    init_code = "@256\nD=A\n@SP\nM=D"
    return init_code

# label
def write_label(command, function_name):
    translation = f"({function_name}${command.split()[1]})"
    translation += f" // {command.split()[1]} label set"
    return translation

#goto
def write_goto(lookups,command, function_name):
    command_parts = command.split()
    translation = lookups[command_parts[0]].format(function_name=function_name, label_name=command_parts[1])
    translation += f" // goto {function_name}.{command_parts[1]}"
    return translation

#if-goto
def write_ifgoto(lookups, command, function_name):
    command_parts = command.split()
    translation = lookups[command_parts[0]].format(function_name=function_name, label_name=command_parts[1])
    translation += f" // ifgoto {function_name}.{command_parts[1]}"
    return translation

#function
def write_function(lookups, command):
    function_name = command.split()[1]
    translation = f"({command.split()[1]})\n"
    arguments = int(command.split()[2])
    for i in range(arguments):
        translation += lookups["func_args"] + "\n"
    translation += f"// function {function_name}"
    return translation, function_name

# return
def write_return(lookups,command):
    translation = lookups[command.split()[0]].format()+"\n"
    for i, segment in enumerate(segments2):
        translation += f"@R13\nAM=M-1\nD=M\n@{segments[segment]}\nM=D\n"
    translation += "@R15\nA=M\n0;JMP"
    translation += f"// return"
    return translation

# call
def write_call(lookups,command, callcount):
    callcount +=1
    command_parts = command.split()
    returnaddress = f"{command_parts[1]}${callcount}" # set the returnadress to come back to later
    translation = lookups[command_parts[0]].format(returnaddress=returnaddress)+"\n" # write "call"
    for i, segment in enumerate(segments):
        translation += f"@{segments[segment]}\nD=M\n"+lookups["segment"]+"\n" # write all segments onto the stack
    arguments = str(int(command_parts[2])+5)
    translation += lookups["args"].format(arguments=arguments,
                                          function_name=command_parts[1],
                                          returnaddress=returnaddress)
    translation += f"// called function {command_parts[1]}"
    # translation += f"@{function_name}${callcount}\n0;JMP"
    return translation, callcount

# push and pop
def write_push_pop(lookups, command, file_name):
    command_parts = command.split()
    segments = {"local":"LCL", "argument":"ARG", "this":"THIS", "that":"THAT", "temp":"5", "pointer":"3", "static":f"{file_name}.{command_parts[-1]}"}
    if command_parts[0] == "push":
        if command_parts[1] == "constant":
            translation = lookups[command_parts[0]].format(integer=command_parts[2])
        else:
            if command_parts[1] == "temp" or command_parts[1] == "pointer" or command_parts[1] == "static":
                insert = "D=D+A\nA=D"
            else:
                insert = "D=D+M\nA=D"
            translation = lookups["push2"].format(integer=command_parts[2], insert=insert, segment=segments[command_parts[1]])
            
    else:
        if command_parts[1] == "temp" or command_parts[1] == "pointer" or command_parts[1] == "static":
            insert = "D=D+A"
        else:
            insert = "D=D+M"
        translation = lookups[command_parts[0]].format(integer=command_parts[2], segment=segments[command_parts[1]], insert=insert)
    return translation

# arithmetic
def write_arithmetic(lookups, command, cmd_tracker):
    cmd_tracker[command] +=1
    repeats = cmd_tracker[command]
    translation = lookups[command].format(repeats=repeats)

    return translation, cmd_tracker