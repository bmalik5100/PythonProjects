""" creates a simple encryption for small file or all files in a folder """
import sys
import os
import ctypes
from pwd import getpwuid
from getpass import getuser
from cryptography.fernet import Fernet
from tkinter import *
from tkinter import filedialog, messagebox

KEY_PATH = ""
ALTER_LOCATION = ""
MODE = ""

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
    except MemoryError:
        return "Memory Failure (File probably too large)"
    except: # catch all
        return "Misc Failure"

def check_privileges():
    """ cross platform check of heightened privileges """
    try: # tries linux/unix
        is_admin = os.geteuid() == 0
    except AttributeError: # tries windows
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

def get_ownership(file_name):
    try:
        file_owner = getpwuid(os.stat(file_name).st_uid).pw_name
    except:
        file_owner = os.stat(file_name).st_uid
    if file_owner == getuser():
        return True
    else:
        return False



def main(mode_switch):
    """ checks for all the discrepencies. If none found, calls alteration functions """

    # Usage and permissions check
    #if not check_privileges():
    #    print("Use prohibited to root/admin users only. Elevate your privileges and try again...")
    #elif len(sys.argv) != 4:
    #    print('Usage: basic_hide -[e/d] [path to directory/file] [path to key]')
    #    print("-e/-d - encrypt/decrypt the directory")

    # Passes global constants to inner function variables
    if mode_switch == 1:
        alter_mode = '-e'
    elif mode_switch == 2:
        alter_mode = '-d'
    else: # catch all
        alter_mode = '-e'

    thing_to_alter = ALTER_LOCATION
    alter_key = KEY_PATH

    # Checks for certain file errors
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
        if thing_to_alter[len(thing_to_alter) - 4:] != ".key": # makes sure key is not encrypted
            print(alter_file(alter_mode, alter_key, thing_to_alter))
        else:
            print(thing_to_alter + " determined as key file. Cannot encrypt...")
    else:
        print("Something went wrong. Try again")
#main()

def get_key_file():
    """ opens file selection box for key files """
    global KEY_PATH
    KEY_PATH = filedialog.askopenfilename(filetypes=(("Key files", "*.key"), ("all files", "*.*")))
    if "/" in KEY_PATH:
        key_name = (KEY_PATH.rsplit("/", 1))[1]
    elif "\\" in KEY_PATH:
        key_name = (KEY_PATH.rsplit("\\", 1))[1]
    else:
        key_name = KEY_PATH
    alter_text = Label(text=f"Key {key_name} loaded.")
    alter_text.pack()

def get_directory():
    """ opens directory selection box """
    global ALTER_LOCATION
    ALTER_LOCATION = filedialog.askdirectory()
    if "/" in ALTER_LOCATION:
        stripped_location = (ALTER_LOCATION.rsplit("/", 1))[1]
    elif "\\" in ALTER_LOCATION:
        stripped_location = (ALTER_LOCATION.rsplit("\\", 1))[1]
    else:
        stripped_location = ALTER_LOCATION
    alter_text = Label(text="Location: " + stripped_location)
    alter_text.pack()

def get_single_file():
    """ opens file selection box for alteration file """
    global ALTER_LOCATION
    ALTER_LOCATION = filedialog.askopenfilename(filetypes=(("all files", "*.*"),
                                                           ("Text files", "*.txt"),
                                                           ("Comma Seperated Values", "*.csv"),
                                                           ("Rich Text Files", "*.rtf"),
                                                           ("JPEG Files", "*.jpeg")))
    if "/" in ALTER_LOCATION:
        stripped_location = (ALTER_LOCATION.rsplit("/", 1))[1]
    elif "\\" in ALTER_LOCATION:
        stripped_location = (ALTER_LOCATION.rsplit("\\", 1))[1]
    else:
        stripped_location = ALTER_LOCATION
    alter_text = Label(text="File to encrypt: " + stripped_location)
    alter_text.pack()

#if not check_privileges():
if False:
    messagebox.showinfo("ERROR", "Use prohibited to root/admin users only.")
else:
    screen = Tk()
    screen.title("Basic Hide")
    screen.geometry("500x300")

    welcome_text = Label(text="Welcome to the Basic Hide GUI\n")
    welcome_text.pack()

    key_button = Button(text="Select Key", command=lambda: get_key_file())
    key_button.pack()

    directory_location_button = Button(text="Select Folder", command=lambda: get_directory())
    directory_location_button.place(x=110, y=75)

    file_location_button = Button(text="Select File", command=lambda: get_single_file())
    file_location_button.place(x=280, y=75)

    or_text = Label(text="\nor")
    or_text.pack()

    encryption_button = Button(text="ENCRYPT", command=lambda: main(1))
    encryption_button.place(x=110, y=165)

    decryption_button = Button(text="DECRYPT", command=lambda: main(2))
    decryption_button.place(x=280, y=165)

    screen.mainloop()
