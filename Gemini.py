import os

# 1. DEFINE YOUR MASTER STRUCTURE HERE
# The list of devices/subsystems
MOTORS = [f"MOTOR_{i}" for i in range(1, 9)]  # MOTOR_1 to MOTOR_8

# The unique actions they can perform
MOTOR_ACTIONS = ["OFF", "SET"]
SERVO_ACTIONS = ["OFF","SET","GET"]

# 2. GENERATE THE C++ HEADER FILE
def generate_arduino_header():
    header_content = """// AUTOMATICALLY GENERATED FILE - DO NOT EDIT DIRECTLY
#ifndef COMMANDS_H
#define COMMANDS_H

// Sequential Command Enums (Each gets assigned a unique byte automatically)
enum Command : byte {
"""
    # Create entries like: MOTOR_1_OFF, MOTOR_1_SET_POWER, etc.
    command_list = []
    for motor in MOTORS:
        for action in MOTOR_ACTIONS:
            command_list.append(f"  {motor},{action}")
            
    header_content += ",\n".join(command_list)
    header_content += "\n};\n\n#endif"

    # Save to your Arduino project folder
    with open("commands.h", "w") as f:
        f.write(header_content)
    print("✓ Successfully generated commands.h for Arduino!")

# 3. GENERATE THE PYTHON DICTIONARY DYNAMICALLY
# This creates a lookup table mapping string inputs to their corresponding enum byte values
command_index = 0
PYTHON_COMMAND_DICT = {}

for motor in MOTORS:
    for action in ACTIONS:
        # Key: "MOTOR_1_OFF" -> Value: 0, 1, 2... encoded as a single raw byte
        key = f"{motor}_{action}"
        PYTHON_COMMAND_DICT[key] = bytes([command_index])
        command_index += 1

if __name__ == "__main__":
    generate_arduino_header()