""" makes a unique key. thats all. """
import sys
import os
from cryptography.fernet import Fernet

if len(sys.argv) != 2:
    print("Usage: generate_key.py [name of key]")
    sys.exit()

name = sys.argv[1]
print(name)

def write_key(file_name):
    """ generates key and saves to root folder """
    key_bits = Fernet.generate_key()
    with open(file_name, "wb") as key_file:
        key_file.write(key_bits)

def load_key(file_name):
    """ loads created key to memory """
    return open(file_name, "rb").read()

if os.path.isfile(name):
    print("Key already exists. Try again.")
    sys.exit()
else:
    try:
        write_key(name)
        key = load_key(name)
        enc = Fernet(key)
        MESSAGE = "Key written successfully.".encode()
        encrypted_message = enc.encrypt(MESSAGE)
        decrypted_message = enc.decrypt(encrypted_message)
        print(decrypted_message.decode("utf-8"))
    except PermissionError:
        print("Permission error...")
    except:
        print("Unknown error...")