""" creates a simple encryption for small file or all files in a folder """
import sys
import os
import ctypes
from cryptography.fernet import Fernet

def load_key(file_name):
    """ tries complete load of key """
    try:
        open(file_name, "rb").read()
    except PermissionError:
        print("Unable to load key file...\nTry again.")
        sys.exit()
    except FileNotFoundError:
        print("Unable to locate key file...\nTry again.")
        sys.exit()

def alter_all(mode, key, directory):
    """ builds a recursive list of all files and folders inside directory
    and calls alter_file function on each """
    entire_directory = []
    for root, dirs, files in os.walk(directory):
        for alt_f in files:
            entire_directory.append(os.path.join(root, alt_f))
    for alt_file in entire_directory:
        if ".key" in alt_file:
            print(alt_file + " determined as key file. Skipping...")
        elif str(__file__) in str(alt_file):
            print("This program cannot alter itself. Skipping...")
        else:
            print(alter_file(mode, key, alt_file))



def alter_file(mode, key, file_name):
    """ alters single file using encryption key provided """
    try:
        with open(key, "rb") as key_file:
            key_data = key_file.read()
        fern = Fernet(key_data)
        with open(file_name, "rb") as old_file:
            file_data = old_file.read()

        if mode == '-e':
            print("Trying encryption of " + file_name + "...", end="")
            encrypted_data = fern.encrypt(file_data)
            with open(file_name, "wb") as new_file:
                new_file.write(encrypted_data)
        elif mode == '-d':
            print("Trying decryption of " + file_name + "...", end="")
            decrypted_data = fern.decrypt(file_data)
            with open(file_name, "wb") as new_file:
                new_file.write(decrypted_data)
        return "Success"
    except PermissionError:
        return "Permission Failure"
    except: # catch all
        return "Misc Failure"

def check_privileges():
    """ cross platform check of heightened privileges """
    try: # tries linux/unix
        is_admin = os.geteuid() == 0
    except AttributeError: # tries windows
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin



def main():
    """ checks for all the discrepencies. If none found, calls alteration functions """

    # Usage and permissions check
    if not check_privileges():
        print("Use prohibited to root/admin users only. Elevate your privileges and try again...")
    elif len(sys.argv) != 4:
        print('Usage: basic_hide -[e/d] [path to directory/file] [path to key]')
        print("-e/-d - encrypt/decrypt the directory")

    # Initializes command line arguments as variables
    alter_mode = str(sys.argv[1])
    thing_to_alter = sys.argv[2]
    alter_key = sys.argv[3]

    if alter_mode != '-e' and alter_mode != '-d':
        print("Incompatible flag...\nAcceptable flags are -e for encryption or -d")
    elif not os.path.isfile(alter_key):
        print("Missing or incorrect key file...\nTry again.")
    elif not os.path.exists(thing_to_alter):
        print("File/Directory does not exist...\nTry again.")
        sys.exit()
    elif __file__ in thing_to_alter:
        print("This program cannot alter itself...")


    elif os.path.isdir(thing_to_alter): # assumes everything works and directory must be encrypted
        try:
            load_key(alter_key)
        except FileNotFoundError:
            print("Cannot load key file...\nTry again.")
            sys.exit()
        except PermissionError:
            print("Permission error...\nTry again.")
            sys.exit()
        alter_all(alter_mode, alter_key, thing_to_alter)

    elif os.path.isfile(thing_to_alter): # assumes everything works and single file
        load_key(alter_key)
        if ".key" not in alter_key: # makes sure key is not encrypted
            print(alter_file(alter_mode, alter_key, thing_to_alter))
        else:
            print(thing_to_alter + " determined as key file. Cannot encrypt...")

    else:
        print("Something went wrong. Try again")
main()
