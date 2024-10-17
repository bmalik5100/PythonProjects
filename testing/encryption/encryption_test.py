# Hash conversion - for sensitive text. Can be bruteforced with dictionary list
import hashlib
import binascii

crypt = hashlib.md5() # can use any algorithm, not just md5 - to find, use print(hashlib.algorythms_available)
offset = b"+securitykey"
password = b"hello"
crypt.update(password + offset) # salting - adding characters to end of string to scramble 
print(crypt)
print(crypt.hexdigest)

# better to use hashlib.pbkdf2_hmac - look it up

dk = hashlib.pbkdf2_hmac('sha256', b'password',b'salt',10000) 
print(binascii.hexlify(dk))