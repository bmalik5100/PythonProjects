import subprocess
import netifaces
import sys
import os

from sqlalchemy import true

# Check sudo
if os.geteuid() != 0:
    print("Error: Run as root.")
    sys.exit()

# parse args
args = sys.argv
if len(sys.argv) != 2:
    print("Wrong number of args.\nTry changemac help")
mode = sys.argv[1].lower()
print(f'Mode: {mode}')
for adapter in netifaces.interfaces()[1:]:
    if mode == "forcerandom":
        os.system(f"ifconfig {adapter} down")
        os.system(f"macchanger -r {adapter}") #randomizes MAC
        os.system(f"ifconfig {adapter} up")    

    if netifaces.AF_INET in netifaces.ifaddresses(adapter) and mode != "forcerandom":
        print(f"{adapter} is online.")
        os.system(f"ifconfig {adapter} down")
        if mode is "random":
            os.system(f"macchanger -s {adapter} | echo")
            os.system(f"macchanger -r {adapter}") #randomizes MAC
        os.system(f"ifconfig {adapter} up")