""" hide_gui_aes.py - creates an AES 356-bit encryption for a general file or files in a folder """
import sys
import os
import ctypes
from getpass import getuser
from random import randint
from datetime import datetime
import PySimpleGUI as sg
from general_encrypt import remove_file_extension as rfe, get_file_extension as gfe
from general_encrypt import  AES_256_decrypt as aesdec, AES_256_encrypt as aesenc
from general_encrypt import generate_fernet_key as gfk

def load_key(file_name):
    """ tries complete load of key """
    try:
        password = open(file_name, "rb").read()
    except PermissionError:
        print("Unable to load key file. Try again.")
    except FileNotFoundError:
        print("Unable to locate key file. Try again.")
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
    enc_ext = ".mqs"

    try:
        with open(file_name, "rb") as old_file:
            file_data = old_file.read()
        
        file_just_name = os.path.split(file_name)[1]
        
        if mode == 'e':
            print("Trying encryption of " + file_just_name + "...", end="")
            encrypted_data = aesenc(file_data, key_data)
            with open(file_name, "wb") as new_file:
                new_file.write(encrypted_data)
            os.rename(file_name, file_name + enc_ext) # adds encryption mark
        
        elif mode == 'd':
            print("Trying decryption of " + file_just_name + "...", end="")
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
        return "Wrong Filetype (Should be " + enc_ext + ")."
    except Exception as err_msg: # catch all
        return "Misc Failure: " + str(err_msg)

def check_privileges():
    """ cross platform check of heightened privileges """
    try: # tries linux/unix
        is_admin = os.geteuid() == 0
    except AttributeError: # tries windows
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def main(key_path, alter_location, mode_switch):
    """ checks for all the discrepencies. If none found, calls alteration functions """

    # makes mode more readable
    if mode_switch == 1:
        alter_mode = 'e'
    elif mode_switch == 2:
        alter_mode = 'd'

    # local 'global' variables
    thing_to_alter = alter_location
    alter_key = key_path

    # Checks for certain file errors
    if not os.path.isfile(alter_key):
        print("Missing or incorrect key file. Try again.")
    elif not os.path.exists(thing_to_alter):
        print("File/Directory does not exist. Try again.")
    elif __file__ in thing_to_alter:
        print("This program cannot alter itself.")

    # encrypts multiple files
    elif os.path.isdir(thing_to_alter): 
        key_data = load_key(alter_key)
        alter_all(alter_mode, key_data, thing_to_alter)

    # encrypts single file
    elif os.path.isfile(thing_to_alter):
        key_data = load_key(alter_key)
        if gfe(thing_to_alter) != ".key":
            print(alter_file(alter_mode, alter_key, thing_to_alter))
        else:
            print(thing_to_alter + " determined as key file. Cannot encrypt.")
    
    # Catch all
    else:
        print("Something went wrong. Try again.")

def pick_ui_theme():
    """ chooses random UI theme from list """
    themes = ["DarkBlue4", "DarkGrey", "DarkTeal10", "DarkBrown4", "Kayak"]
    num = randint(0, len(themes) - 1)
    return themes[num]

def save_file(filename, info):
    """ adds some structure and saves debug info to a file """
    with open(filename, 'w') as save_file:
        now = datetime.now().strftime(("%m/%d/%Y, AT %H:%M:%S"))
        save_file.write(f'\tLOG FOR {now}\n')
        save_file.write(info)
        save_file.write('\n--')

def make_ui():
    """ Creates window loop """
    # GUI layout info
    print = sg.Print
    sg.theme(pick_ui_theme())
    key_path = ""
    alter_location = ""
    menu_items = [['File', ['Save log', 'Generate Key', 'Exit']]]

    file_list_column = [
        [
            sg.Text("   Key File", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-KEY-FILE-"),
            sg.FileBrowse(file_types=(("Key Files", '*.key'), ("All Files", '*.*')))
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("  Directory", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Text("Single File", justification="center"),
            sg.In(size=(25, 1), enable_events=True, key="-SINGLE-FILE-"),
            sg.FileBrowse(file_types=(("All Files", '*.*'), ("Text Files", "*.txt")))
        ]
    ]

    button_column = [
        [
            sg.T('    '),
            sg.Button(button_text="ENCRYPT", size=(12, 3), key="-ENCRYPTION-"),
            sg.Button(button_text="DECRYPT", size=(12, 3), key="-DECRYPTION-")
        ]
    ]

    layout = [
        [sg.Menu(menu_items)],
        [
            sg.Column(file_list_column, justification="center"),
            sg.VSeperator(),
            sg.Column(button_column)
        ],
        [sg.Output(size=(600, 50), background_color="LightGrey", text_color="Black", key='-DEBUG-')]
    ]
    try:
        window = sg.Window("Laputa: AES 256-Bit Encryption Tool", size=(700, 300), icon='icon.ico').Layout(layout)
    except FileNotFoundError:
        window = sg.Window("Laputa: AES 256-Bit Encryption Tool", size=(700, 300)).Layout(layout)
    old_key_path = ''

    # Event Loop
    while True:
        event, values = window.read()

        # Exit conditions
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
        # Key file event
        elif event == "-KEY-FILE-":
            key_path = str(values["-KEY-FILE-"])
            if key_path != old_key_path and key_path != '':
                info = window['-DEBUG-'].Get()
                key_name = os.path.split(key_path)[1]
                window['-DEBUG-'].Update(info[:len(info)-1] + f'Loaded key: {key_name}.\n')
            old_key_path = key_path

        # Folder event
        elif event == "-FOLDER-":
            alter_location = values["-FOLDER-"]
            if alter_location and alter_location != '':
                info = window['-DEBUG-'].Get()
                single_folder = os.path.split(alter_location)[1]
                window['-DEBUG-'].Update(info[:len(info)-1] + f'Loaded folder: {single_folder}.\n')

        # Single File Event
        elif event == "-SINGLE-FILE-":
            alter_location = values["-SINGLE-FILE-"]
            if alter_location and alter_location != '':
                info = window['-DEBUG-'].Get()
                alter_name = os.path.split(alter_location)[1]
                window['-DEBUG-'].Update(info[:len(info)-1] + f'Loaded file: {alter_name}.\n')

        # Save event
        elif event == "Save log":
            name = sg.filedialog.asksaveasfilename()
            info = window['-DEBUG-'].Get()
            if name and len(info) != 0:
                save_file(name, info)

        # Keygen
        elif event == 'Generate Key':
            name = sg.filedialog.asksaveasfilename(filetypes=[("Key files", "*.key")])
            if len(name) != 0:
                gfk(name)

        # Main event
        elif event == "-ENCRYPTION-" or event == "-DECRYPTION-":
            if len(key_path) == 0:
                sg.popup("Please select a key file.")
            elif gfe(key_path) != ".key":
                sg.popup("Please select a valid key file.")
            if event == "-ENCRYPTION-":
                main(key_path, alter_location, 1)
            elif event == "-DECRYPTION-":
                main(key_path, alter_location, 2)
    window.close()

make_ui()
