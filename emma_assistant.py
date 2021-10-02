from emma_core import emma
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import json
import requests
import sys
import checkers
import emma_core
from gtts import gTTS
import playsound


if len(sys.argv) > 1:
    if sys.argv[1] == "--voice" or sys.argv[1] == "voice":
        try:
            import speech_recognition as sr
            mode = "voice"
        except ImportError:
            print(
                "\nInstall SpeechRecognition to use this feature.\nStarting text mode\n")


Emma_Core = emma.Emma()

while(1):

    input = {'text', 'lang'}
    output = {'text': str, 'dest_lang': 'en'}

    # check internet connection status
    Emma_Core.check_internet_connection()

    # listen
    input = dict(Emma_Core.listen())

    # check internet connection
    # conditions
    if Emma_Core.internet_connection:
        pass

    if output['text'] == None:
        if checkers.show_time_checker(input):
            output['text'] = Emma_Core.show_datetime()['time']

        else:
            output['text'] = Emma_Core.aiml_response(input)

    # speech
    if Emma_Core.internet_connection:
        Emma_Core.speak_gtts(output['text'],dest_lang=output['dest_lang'])
    else:
        Emma_Core.speak_pyttsx3(output['text'],dest_lang=output['dest_lang'])
