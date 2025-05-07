import argparse
import os

# translations
def command_translation(command):
    command_parts = command.split()
    # command_parts[0]
    if command_parts[0] == "push":
        translation = f"""@{command_parts[2]}
D=A
@SP
AM=M+1
A=A-1
M=D"""
    else:
        pass
    return translation

def trans_arithmetic(command):
    if command == "add":
        translation="""@SP
AM=M-1
D=M
A=A-1
M=M+D"""
    else:
        pass
    return translation
    

# segment_translations

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in",
        "--input_file",
        required=True,
        help="VM file translated to hack language",
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

    vm_commands = []
    for command in vm_commands_stripped:
        if len(command.split()) < 2:
            #hier Arithmetische Rechnungen und Zuordnung
            vm_commands.append(trans_arithmetic(command))
        else:
            # hier in die 3 Segmente aufteilen und jeweils zuordnen und übersetzen
            translated_command = command_translation(command)
            vm_commands.append(translated_command)

    # Save translated code.
    out_file_name = os.path.basename(args.input_file).split(".")[0] + ".asm"
    out_path = os.path.dirname(args.input_file)
    with open(os.path.join(out_path, out_file_name), "w") as f:
        f.writelines([str(command) + "\n" for command in vm_commands])
