""" creates a simple encryption for small file or all files in a folder """
import sys
import os
import ctypes
from getpass import getuser
from random import randint
import PySimpleGUI as sg
from general_encrypt import remove_file_extension as rfe, get_file_extension as gfe
from general_encrypt import  AES_256_decrypt as aesdec, AES_256_encrypt as aesenc

def load_key(file_name):
    """ tries complete load of key """
    try:
        password = open(file_name, "rb").read()
    except PermissionError:
        print("Unable to load key file...\nTry again.")
        sys.exit()
    except FileNotFoundError:
        print("Unable to locate key file...\nTry again.")
        sys.exit()
    return password


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
    if mode == 'd':
        print("Directory decryption completed.")
    else:
        print("Directory encryption completed.")

def alter_file(mode, key_data, file_name):
    """ alters single file using encryption key provided """
    enc_ext = ".ael"

    try:
        with open(file_name, "rb") as old_file:
            file_data = old_file.read()

        if mode == 'e':
            print("Trying encryption of " + file_name + "...", end="")
            encrypted_data = aesenc(file_data, key_data)
            with open(file_name, "wb") as new_file:
                new_file.write(encrypted_data)
            os.rename(file_name, file_name + enc_ext) # adds encryption mark

        elif mode == 'd':
            print("Trying decryption of " + file_name + "...", end="")
            if gfe(file_name) != enc_ext: # checks for encryption mark
                raise ZeroDivisionError
            else:
                decrypted_data = aesdec(file_data, key_data)
                with open(file_name, "wb") as new_file:
                    new_file.write(decrypted_data)
                os.rename(file_name, rfe(file_name)) # removes encryption mark

        return "Success"
    except PermissionError:
        return "Permission Failure"
    except MemoryError:
        return "Memory Failure (File probably too large)"
    except ZeroDivisionError:
        return "Wrong Filetype for decryption (Should be " + enc_ext + ")."
    except Exception as err_msg: # catch all
        return "Misc Failure: " + str(err_msg)

def check_privileges():
    """ cross platform check of heightened privileges """
    try: # tries linux/unix
        is_admin = os.geteuid() == 0
    except AttributeError: # tries windows
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def get_ownership(file_name): # WIP because of dumbass cross-platform bugs
    try:
        #file_owner = getpwuid(os.stat(file_name).st_uid).pw_name
        pass
    except:
        file_owner = os.stat(file_name).st_uid
    if file_owner == getuser():
        return True
    else:
        return False

def main(key_path, alter_location, mode_switch):
    """ checks for all the discrepencies. If none found, calls alteration functions """

    # Usage and permissions check
    #if not check_privileges():
    #    print("Use prohibited to root/admin users only. Elevate your privileges and try again...")
    #    time.sleep(3)
    #    sys.exit()

    if mode_switch == 1:
        alter_mode = 'e'
    elif mode_switch == 2:
        alter_mode = 'd'
    else: # catch all
        alter_mode = 'e'

    thing_to_alter = alter_location
    alter_key = key_path

    # Checks for certain file errors
    if not os.path.isfile(alter_key):
        print("Missing or incorrect key file...\nTry again.")
    elif not os.path.exists(thing_to_alter):
        print("File/Directory does not exist...\nTry again.")
    elif __file__ in thing_to_alter:
        print("This program cannot alter itself...")

    elif os.path.isdir(thing_to_alter): # assumes everything works and directory must be encrypted
        key_data = load_key(alter_key)
        alter_all(alter_mode, key_data, thing_to_alter)

    elif os.path.isfile(thing_to_alter): # assumes everything works and single file
        key_data = load_key(alter_key)
        if gfe(thing_to_alter) != ".key": # makes sure key is not encrypted
            print(alter_file(alter_mode, alter_key, thing_to_alter))
        else:
            print(thing_to_alter + " determined as key file. Cannot encrypt...")
    else:
        print("Something went wrong. Try again")


def pick_ui_theme():
    """ chooses random ui theme from list """
    themes = ["DarkBlue4", "DarkGrey", "DarkTeal10", "DarkBrown4"]
    num = randint(0, len(themes) - 1)
    return themes[num]

def make_ui():

    sg.theme(pick_ui_theme())

    key_path = ""
    alter_location = ""

    file_list_column = [
        [
            sg.Text("Key File", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-KEY-FILE-"),
            sg.FileBrowse(file_types=(("Key Files", '*.key'), ("All Files", '*.*')))
        ],
        [
            sg.Text("Directory", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [sg.T("\t\t   "), sg.Text("or", justification="right")],
        [
            sg.Text("Single File", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-SINGLE-FILE-"),
            sg.FileBrowse(file_types=(("All Files", '*.*'), ("Text Files", "*.txt")))
        ]
    ]

    button_column = [
        [
            sg.Button(button_text="ENCRYPT", size=(7, 3), key="-ENCRYPTION-"),
            sg.Button(button_text="DECRYPT", size=(7, 3), key="-DECRYPTION-")
        ]
    ]

    # ----- Full layout -----
    layout = [
        [
            sg.Column(file_list_column, justification="right"),
            sg.VSeperator(),
            sg.Column(button_column),
        ],
        [sg.Button(button_text="Exit")]
    ]
    window = sg.Window("AES Encryption", layout)

    # Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED: # Exit conditions
            break
        elif event == "-FOLDER-":
            alter_location = values["-FOLDER-"]
        elif event == "-KEY-FILE-":
            key_path = values["-KEY-FILE-"]
        elif event == "-SINGLE-FILE-":
            alter_location = values["-SINGLE-FILE-"]
        elif event == "-ENCRYPTION-" or event == "-DECRYPTION-":
            if len(key_path) == 0:
                sg.popup("Please Select a key file.")
            elif gfe(key_path) != ".key":
                sg.popup("Please select a valid key file.")
            if event == "-ENCRYPTION-":
                main(key_path, alter_location, 1)
            elif event == "-DECRYPTION-":
                main(key_path, alter_location, 2)
    window.close()

make_ui()
