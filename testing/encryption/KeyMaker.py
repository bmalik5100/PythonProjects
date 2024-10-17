import sys
import os
from cryptography.fernet import Fernet
from tkinter import *

def write_key(file_name):
    """ generates key and saves to root folder """
    key_bits = Fernet.generate_key()
    with open(file_name, "wb") as key_file:
        key_file.write(key_bits)

def load_key(file_name):
    """ loads created key to memory """
    return open(file_name, "rb").read()


def generate_key(name):
    """ creates the key, checks for errors, and verifies with encrypted/decrypted message """
    if ".key.key" in name:
        name = name[:len(name)-4]

    if len(name) == 4 or len(name) > 64:
        err_msg = Label(text="Inappropriate name length...", fg="red")
        err_msg.pack()

    elif '\\' in name or '/' in name or ':' in name or '*' in name or '?' in name or '"' in name or '<' in name or '>' in name or "|" in name:
        err_msg = Label(text="Inappropriate character in name. Unsupported characters: \\/:*?\"<>|",
                        fg="red")
        err_msg.pack()

    elif os.path.isfile(name):
        duplicate_error = Label(text="Key already exists. Try again.", fg="red")
        duplicate_error.pack()
    else:
        try:
            write_key(name)
            key = load_key(name)
            enc = Fernet(key)
            message = " written successfully.".encode()
            encrypted_message = enc.encrypt(message)
            decrypted_message = enc.decrypt(encrypted_message)
            success_message = decrypted_message.decode("utf-8")
            success = Label(text=name+success_message, fg="green")
            success.pack()
        except PermissionError:
            err_msg = Label(text="Permission error...", fg="red")
            err_msg.pack()
        except:
            err_msg = Label(text="Unknown error...", fg="red")
            err_msg.pack()


screen = Tk()
screen.title("KeyMaker")
screen.geometry("500x300")

welcome_text = Label(text="Enter name of encryption key:")
welcome_text.pack()

name = StringVar()
name_label = Entry(textvariable=name)
name_label.pack()

format_text = Label(text="Key written in *.key format.")
format_text.pack()

try:
    screen.wm_iconbitmap('keymakericon.ico')
except TclError:
    pass

generator = Button(text="Generate Key", command=lambda: generate_key(name.get() + ".key"))
generator.pack()

screen.mainloop()
