"""

Icon credit goes to bqlqn and Freepik from flaticon.com

"""

import os
import pocketsphinx
import pyttsx3
import random
import speech_recognition as sr
import threading

from datetime import datetime
from cleverwrap import CleverWrap
from html.parser import HTMLParser
from io import BytesIO
from sys import platform

API_KEY = "" # REDACTED

voice = None
brain = None
attention = None
recording = sr.Recognizer()
#print = sg.Print

    

def conversation_loop():
    global voice, brain, attention
    

    while True:
       print("You: ", end='')
       client_sound = input()
       response = attention.say(client_sound)
       print("Martha: " + response)
       voice.say(response)
       voice.runAndWait()
       voice.stop()

def get_client_sound():
    global recording
    print("Recording...")
    with sr.Microphone() as source:
        audio = recording.listen(source)
        while True:
            try:
                return recording.recognize_sphinx(audio)
            except sr.UnknownValueError:
                print("Error: I could not understand you")
            except sr.RequestError as e:        
                print("Sphinx error; {0}".format(e))

def initialize():
    global voice, brain, API_KEY, attention
    
    voice = pyttsx3.init()

    if platform == 'linux' or platform == 'linux2':
        voice.setProperty('voice', 'english_rp+f3')
    elif platform == 'win32':
        voice.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
    
    voice.setProperty('rate', 120)
    brain = CleverWrap(API_KEY)
    attention = brain.new_conversation()

def new_conversation():
    global attention
    attention.reset()

def pick_ui_theme():
    """ chooses random ui theme from list """
    themes = ["DarkBlue4", "DarkGrey", "DarkTeal10", "DarkBrown4"]
    num = random.randint(0, len(themes) - 1)
    return themes[num]

def query_greeting():
    global voice
    greetings = ["Where have you been?", "What's up?", "Welcome back.", "You're back!", "How's it?", "Hey, you!"]
    greeting = greetings[random.randrange(len(greetings))]
    print("Martha: " + greeting)
    voice.say(greeting)
    voice.runAndWait()
    voice.stop()

def save_file(filename, info):
    """ adds some structure and saves debug info to a file """
    with open(filename, 'w') as save_file:
        now = datetime.now().strftime(("%m/%d/%Y, AT %H:%M:%S"))
        save_file.write(f'\tLOG FOR {now}\n')
        save_file.write(info)
        save_file.write('\n--')

def main():
    initialize()
    query_greeting()
    conversation_loop()

main()
