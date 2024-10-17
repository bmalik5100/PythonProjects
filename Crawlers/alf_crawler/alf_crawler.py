# "Crawls" through multiple homestuck webpages to grab conversation logs
# and convert it into jsonl data to train a gpt3 ada bot 
# TODO add threading (ew)
import requests
import logging
import time
import glob
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

DYNAMIC_ITERATION = True # gets most recent page parsed from the log file and picks up from there  
DATE = datetime.now() # timestamp info
LOGFILE = __file__.replace("homestuck_crawler.py" ,f"Logs/hc{DATE.strftime('%Y%m%d')}.log")# path where log file will be created
MAXPAGE = 9000 # This is probably all we need
STARTPAGE = 26 # First page with chat diologue
REQUESTDELAY = 1 # how many seconds to delay each http request (hopefully diverts cloudflare 403 for 7 req/sec)
logger = logging.getLogger()
logging.basicConfig(filename=LOGFILE, filemode="a", level=logging.INFO, format='%(levelname)s - %(message)s')

def getRecentPage():
    """ Picks up where you left off :) """
    latest_file = max(glob.glob(__file__.replace("homestuck_crawler.py", "/Logs/*")), key=os.path.getctime)
    with open(latest_file, "r") as lf:
        file_data_r =  lf.readlines()[::-1]

    for line in file_data_r:
        if "Final page parsed: " in line:
            begin = len("INFO - Final page parsed: ")
            most_recent_page = line[begin: -1]
            if most_recent_page.isdigit():
                next_page = int(most_recent_page) + 1
                logger.info(f"Starting at page: {next_page}")
                return next_page
            break

    return STARTPAGE

def convertToJsonl(logs, prompter, responder):
    index = 1
    # combine all messages sent sepearately to one msg,
    # such that users take turns sending msgs
    while index < len(logs):
        if logs[index - 1]["user"] == logs[index]["user"]:
            logs[index - 1]["message"] += f'. {logs[index]["message"]}'
            logs.pop(index)
        else:
            index += 1

    # convert conversation to GPT-compatible jsonl format
    if logs[0]['user'] == responder: 
        logs.pop(0)

    with open(__file__.replace("homestuck_crawler.py", f'Training Data/{responder}.jsonl'), "a") as jfile:
        for i in range(0, len(logs) - 1, 2): # start at OTHER user's first msg
            try:
                jline = { "prompt" : logs[i]["message"], "completion" : logs[i+1]["message"] }
                jfile.write(f'{jline}\n')
            except IndexError:
                print("index error")
                break
    
    logger.info(f"Collected {len(logs)} lines for user {responder}")

def getConversationSoup(body):
    soup = BeautifulSoup(body, "html.parser")
    chatarea = soup.body.find("p", attrs={"class" : "o_chat-log"})
    

def getConversationLogs(body):
    convo = list()
    users = set()

    if "o_chat-log" in body:
        body = body[slice(body.index("o_chat-log "), body.index("/div", body.index("o_chat-log")))]
        for line in body.split("<br>"):
            try:
                if line.count("-") <= 3 and "<span style=\"color:" in line:
                    user = line[line.index("\">") + 2: line.index(":", line.index("\">"))]
                    msg =  line[line.index(user) + 2 + len(user): line.index("</span>")]
                    users.add(user)
                    if len(users) > 2:
                        return list(), users
                    convo.append({ "user" : user, "message" : msg})

            except ValueError as v:
                print("line ", body.index(line), str(v))
    else:
        return list(), users
    
    print(f"conversation logs for {PAGE}: {len(convo)}\tUsers: {len(users)}")
    return convo, users

if __name__ == "__main__":
    logging.info(f"Starting crawler at {DATE.strftime('%H:%M:%S %Y/%m/%d')}")
    running = True
    PAGE = STARTPAGE if not DYNAMIC_ITERATION else getRecentPage()
    
    # Begin loop
    while running and PAGE <= MAXPAGE:
        
        try:
            html = requests.get(f"https://www.homestuck.com/story/{PAGE}")
            time.sleep(REQUESTDELAY) # hopefully to not trigger cloudflare ban (1 page per second)

            if html.status_code != 200:
                raise requests.exceptions.ConnectionError
            
            logs, users = getConversationLogs(html.content.decode())

            if len(logs) > 0 and len(users) == 2:
                logger.info(f"Got page: {PAGE}")
                try:
                    [primary, secondary] = list(users)
                    convertToJsonl(logs, primary, secondary)
                    convertToJsonl(logs, secondary, primary)
                    logger.info(f"Parsed JSONL data for page {PAGE}")
                except Exception as e:
                    logger.error(f"Could not parse JSONL data for page {PAGE} because of {e}")
            #else:
            #    print(f"Uh oh, {PAGE} count = 0: ", not len(logs) > 0, "\t Users count: ", len(users))
            PAGE += 1
            

        except KeyboardInterrupt:
            end_time = datetime.now()
            logger.info(f"Closed crawler by Keyboard Interrupt at {end_time.strftime('%H:%M:%S %Y/%m/%d')}")
            running = False

        except requests.exceptions.ConnectionError:
            end_time = datetime.now()
            running = False
            logger.error(f"Closed crawler due to connection error at {end_time.strftime('%H:%M:%S %Y/%m/%d')}")

        except Exception as e:
            end_time = datetime.now()
            logger.error(f"Misc error: {e}")
            running = False

    logger.info(f'Time elapsed: {(end_time - DATE).total_seconds()} seconds')
    logger.info(f'Final page parsed: {PAGE}')

else:
    with open("/home/malik/Documents/Scripts/Python/homestuck_crawler/test.html", "r") as f:
       testbody = f.read()
    logs, users = getConversationLogs(testbody)
    users = list(users)
    convertToJsonl(logs, users[0], users[1])
    convertToJsonl(logs, users[1], users[0])
    logger.info(f'Final page parsed: {STARTPAGE}')
    print("did it work?")

    print(getRecentPage())
