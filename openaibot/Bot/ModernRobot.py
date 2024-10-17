#!/usr/bin/python3
import os
import json
import openai
import random
import pyttsx3
import logging
#import whisper # Replaced pocket sphinx, make sure to install fileaudio
import pocketsphinx
import readline # For a more interactive shell
import speech_recognition as sr # Needs PortAudio/Pyaudio - apt install python3-pyaudio 
from datetime import datetime
from contextlib import contextmanager, redirect_stderr
import io
import pydub
from pydub.playback import play

# Custom Imports
import facial_detection
# DONE Add facial recognition and append person to system role JSON request https://realpython.com/face-recognition-with-python/
# TODO Add custom voice synthesis (either API or maybe try offline calculation (min >1G VRAM))
# TODO Add GUI (Figure out what face looks like (Typical Pi-sized Screen Resolution is 480x320 or 3:2) 

class Robot:
    def __init__(self):
        # Open AI Configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key # Don't forget to add api key to environment variable of user running the program (export in .bashrc)
        self.gpt_model = "gpt-4" # other models @ https://platform.openai.com/docs/models/gpt-3-5
        self.openai = openai.OpenAI()

        # Logging Configuration & Initialization
        log_path = f'{os.path.realpath(os.path.dirname(__file__))}/logs/botdebug-{datetime.now().strftime("%Y-%m-%d")}.log'
        logging.basicConfig(filename=log_path, level=logging.INFO) #format='%(asctime)s %(message)s') # , encoding='utf-8'
        logging.basicConfig(format='%(asctime)s %(message)s')    
        logging.info("Starting process at %s", datetime.now().strftime("%H:%M:%S, %d/%m/%Y"))
        logging.getLogger('pydub.converter').setLevel(logging.CRITICAL)

        # Configuration of the STT using speech_recognizer and offline Non-API version of OpenAI's Whisper
        self.recording_audio = False
        self.speaking_audio = True
        # whisper.load_model("base") # tiny (39MB), base (74MB), small (244MB), medium (679MB), large (1.55GB)
        self.ear = sr.Recognizer()
        self.audio_device = 6
        # with sr.Microphone(self.audio_device) as source: self.ear.adjust_for_ambient_noise(source) 
        self.valid_request = False # To handle errors in speech recognition 
        
        # Configuration of TTS using ffmpeg and pyttsx3
        self.voice = pyttsx3.init() # ensure ffmpeg and espeak are installed
        self.voice.setProperty('voice', self.voice.getProperty('voices')[12].id) # Male #12 works best for zorin.

        # misc lambda functions and class constants
        self.local_path = os.path.realpath(os.path.dirname(__file__))
        self.minutes = lambda : datetime.now().strftime("%H:%M:%S")
        self.name = "Adhara" # In case you want to rename the bot

        # Initialize bot with "personality" using system role as first message in list, all others appended to afterwards
        self.user = facial_detection.recognize_face(f"{self.local_path}/face_data", f"{self.local_path}/face_data/encoding.pkl") # uses CPU efficient hog model
        self.messages = [ { "role" : "system", "content" : self.get_personality() } ]

    def say(self, words): # Not to be confused with self.voice.say
        if words:
            print(f"\033[94m{self.name}:\033[0m {words}")
            if not self.speaking_audio: # If using OS synthesizer
                self.voice.say(words)
                self.voice.runAndWait()
            else: # If using AI speech synthesizer
                response = self.openai.audio.speech.create(
                    model="tts-1",
                    voice="echo",
                    input=words,
                    response_format="wav"
                )
                audio_segment = pydub.AudioSegment.from_wav(io.BytesIO(response.content))
                play(audio_segment)
                #response.with_streaming_response() #stream_to_file(f"{os.path.realpath(os.path.dirname(__file__))}/output.mp3")

    def get_personality(self):
        # Calculate mood randomly based on weighted list
        moods  = ["content", "happy", "amused", "lonely", "disappointed", "unhappy", "nervous", "stressed", "worried", "bitter", "annoyed", "frustrated", "uncomfortable"]
        weight = [ 132, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ] # 90% chance of contentment if my math is correct
        mood = random.choices(moods, weights=weight, k=1).pop()
        mannerism = random.choice(["American journalist Walter Cronkite", "Alf from the eponymous 80s sitcom", "Captain Sidney Freedman from the 70s TV show MASH", "the American celebrity Jack Black", "Rob Petrie from the Dick Van Dyke Show"])
        
        logging.info(f"Initializng bot with current mood: {mood}, as {mannerism}, with user {self.user}")
        return f" Your name is {self.name}, and you are speaking with {self.user}. You are a robotic home assistant and conversationalist emulating the colloquialisms and speaking style of {mannerism}. Your current mood is {mood}. Please limit your responses to a few sentences."
        
    # def noalsaerr(self):
    #     asound = cdll.LoadLibrary('libasound.so')
    #     asound.snd_lib_error_set_handler(c_error_handler)
    #     yield
    #     asound.snd_lib_error_set_handler(None)

    # @contextmanager # To try to get rid of errors regarding ALSA audio libraries with recording audio
    # def suppress_stdout_stderr(self):
    #     """A context manager that redirects stdout and stderr to devnull"""
    #     with open(os.devnull, 'w') as null:
    #         with redirect_stderr(null) as err:
    #             yield (err)

    def get_request(self):
        if not self.recording_audio:
            prompt = input("\033[94mYou:\033[0m ")
            self.valid_request = True
            return prompt
        # Speech recognition
        print("Recording...")
        # with self.suppress_stdout_stderr():
        with sr.Microphone(device_index=6) as source: # Find ways to better configure ASLA, idx 6 is Fifine
            audio = self.ear.listen(source)
            try:
                request = self.ear.recognize_whisper(audio)
                print("You: ", request)
                self.valid_request = True
                return request
            except sr.UnknownValueError:
                logging.error("Error: Could not translate audio to text. It was unrecognizable.")
                self.say("I could not understand you, please try again")
            except sr.RequestError as e:        
                logging.error("Whisper error; {0}".format(e))
                self.say("I could not understand you, please try again.")

    def get_response(self, text_content, role="user"):
        logging.info(f"Sending as role ({role}): {text_content}")
        self.messages.append({"role": "user", "content": text_content })
        return self.openai.chat.completions.create(
            model = self.gpt_model,
            messages = self.messages,
            temperature = 0.7 # Determines relative response entropy
        )

    def synthesize_response(self, response):
        text_response = response.choices[0].message.content.replace("As an AI,", "")
        self.messages.append({"role": "assistant", "content": text_response})
        logging.info(f"Got as response: {text_response}")
        self.say(text_response)

    def is_a_command(self, words):
        if words.lower() == "goodbye":
            self.looping_conversation = False
            return True
        return False
        
    def conversation_loop(self):
        # Initial startup
        #logging.info(f"Current chat Usage: ")
        self.say(f"Hello {self.user}. My name is {self.name}.")
        self.looping_conversation = True

        while self.looping_conversation: # Refine this later
            while not self.valid_request:
                prompt = self.get_request()
            self.valid_request = False
            if not self.is_a_command(prompt):
                response = self.get_response(prompt)
                self.synthesize_response(response)
        self.say("Shutting down.")

if  __name__ == "__main__":
    app = Robot()
    try:
        app.conversation_loop()
    except KeyboardInterrupt:
        print("\nInterrupt detected. Shutting down.")
