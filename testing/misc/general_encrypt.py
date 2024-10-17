""" encryption functions for use on local data """
import base64
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from cryptography.fernet import Fernet

BLOCK_SIZE = 16

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def get_private_key(password):
    """ creates private key based on PBKDF2 key derivation function
    on a specified password - returns key """
    salt = b'extra padding'
    kdf = PBKDF2(password, salt, 64, 1000)
    key = kdf[:32]
    return key

def AES_256_encrypt(raw_data, password):
    private_key = get_private_key(password)
    raw_data = pad(raw_data)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw_data))

def AES_256_decrypt(encrypted_data, password):
    private_key = get_private_key(password)
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data[16:]))

def fernet_encrypt(raw_data, key):
    aux = Fernet(key)
    return aux.encrypt(raw_data)

def fernet_decrypt(encrypted_data, key):
    aux = Fernet(key)
    return aux.decrypt(encrypted_data)

def new_file_extension(name, extension):
    """ gives file new extension for specified file """
    dot = name.rfind('.')
    if extension[0] != '.':
        extension = '.' + extension

    if dot == -1:
        return name + extension
    else:
        return name[:dot] + extension

def check_extension(name):
    """ returns extesion of file """
    dot = name.rfind('.')
    if dot == -1:
        raise NameError
    else:
        return name[dot:] 
