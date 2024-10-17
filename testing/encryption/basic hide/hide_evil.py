""" creates a simple encryption for small file or all files in a folder """
import sys
import os
from cryptography.fernet import Fernet
from tkinter import *
from tkinter import filedialog, messagebox

def alter_all(mode, directory):
    """ builds a recursive list of all files and folders inside directory
    and calls alter_file function on each """
    entire_directory = []
    for root, dirs, files in os.walk(directory):
        for alt_f in files:
            entire_directory.append(os.path.join(root, alt_f))

    for alt_file in entire_directory:
        if ".key" in alt_file:
            pass
            #print(alt_file + " determined as key file. Skipping...")
        elif str(__file__) in str(alt_file):
            pass
            #print("This program cannot alter itself. Skipping...")
        else:
            alter_file(mode, alt_file)
    #print("File alteration completed.")



def alter_file(mode, file_name):
    """ alters single file using encryption key provided """
    try:
        key_data = KEY.encode()
        fern = Fernet(key_data)

        with open(file_name, "rb") as old_file:
            file_data = old_file.read()

        if mode == '-e':
            #print("Trying encryption of " + file_name + "...", end="")
            encrypted_data = fern.encrypt(file_data)
            with open(file_name, "wb") as new_file:
                new_file.write(encrypted_data)
        elif mode == '-d':
            #print("Trying decryption of " + file_name + "...", end="")
            decrypted_data = fern.decrypt(file_data)
            with open(file_name, "wb") as new_file:
                new_file.write(decrypted_data)
        #return "Success"
    except PermissionError:
        pass
        #return "Permission Failure"
    except MemoryError:
        pass
        #return "Memory Failure (File probably too large)"
    except: # catch all
        pass
        #return "Misc Failure"

def main(mode_switch):
    """ checks for all the discrepencies. If none found, calls alteration functions """

    # Passes global constants to inner function variables
    if mode_switch == 1:
        alter_mode = '-e'
    elif mode_switch == 2:
        alter_mode = '-d'
    else: # catch all
        alter_mode = '-e'

    thing_to_alter = PATH

    # Checks for certain file errors
    if alter_mode != '-e' and alter_mode != '-d':
        pass
        #print("Incompatible flag...\nAcceptable flags are -e for encryption or -d for decryption")
    elif not os.path.exists(thing_to_alter):
        #print("File/Directory does not exist...\nTry again.")
        sys.exit()
    elif __file__ in thing_to_alter:
        pass
        #print("This program cannot alter itself...")

    elif os.path.isdir(thing_to_alter): # assumes everything works and directory must be encrypted
        alter_all(alter_mode, thing_to_alter)

    elif os.path.isfile(thing_to_alter): # assumes everything works and single file
        if thing_to_alter[len(thing_to_alter) - 4:] == ".key": # makes sure key is not encrypted
            alter_file(alter_mode, thing_to_alter)
        else:
            pass
            #print(thing_to_alter + " determined as key file. Cannot encrypt...")
    else:
        pass
        #print("Something went wrong. Try again")



main(2)
KEY = "5rhIHDNvW9CGKrvYSE3pypfZWuCAxJD8byW_rZ-vmus="
PATH = "~/"

# mode - 1 for encryption
#        2 for decryption

# KEY HISTORY
# Test key (7/2/2020) - 5rhIHDNvW9CGKrvYSE3pypfZWuCAxJD8byW_rZ-vmus=

# DIRECTORY HISTORY
# Test Directory (7/2/2020) - ~/