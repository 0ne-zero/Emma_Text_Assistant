import re
import threading
from gtts import gTTS
from numpy import result_type
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import json
import requests
import aiml
from datetime import datetime
from langid import classify
from googletrans import Translator
import playsound


class Emma:

    def __init__(self, brainFile=None,
                 learnFiles=[], commands=[],
                 chdir=None) -> None:

        self.mode = None
        self.internet_connection = None
        self.__kernel = aiml.Kernel()
        self.__running = None

        self.__kernel.bootstrap(brainFile, learnFiles, commands, chdir)
        self.check_internet_connection()

    # should be run with thread and always running.
    def __check_internet_connection(self):
        '''check internet connection in a thread (always)'''
        def checking_conneciton_status():
            g_ping = os.system('ping4 -c 1 google.com')
            if g_ping == 1:
                y_ping = os.system('ping4 -c 1 yahoo.com')
                if y_ping == 1:
                    self.internet_connection = False

            self.internet_connection = True
        thread = threading.Thread(target=checking_conneciton_status)
        thread.run()

    def check_internet_connection(self):
        '''show internet connection status'''
        g_ping = os.system('ping4 -c 1 google.com')
        if g_ping == 1:
            y_ping = os.system('ping4 -c 1 yahoo.com')
            if y_ping == 1:
                return (False, 'No internet connection')
        return (True, 'internet is connected')

    def speak_gtts(self, text: str, src_lang: str, dest_lang: str):
        '''speak by google text to speech service/api (online)'''
        gtts = gTTS(text)
        gtts.save('emma_speak_voice.mp3')
        playsound.playsound('emma_speak_voice.mp3')

    def speak_pyttsx3(self, text: str, src_lang: str, dest_lang: str):
        '''speak by pyttx3 service (offline)'''
        pyttsx3_engine = pyttsx3.init()
        pyttsx3_engine.say(text)
        pyttsx3_engine.runAndWait()

    def translate_google(self, text: str, src_lang: str, dest_lang: str = 'en'):
        '''translate a text with google translation service/api (online)'''
        t = Translator()
        return t.translate(text, dest_lang).text

    def aiml_response(self, input):
        '''get aiml response by a input'''
        return self.__kernel.respond(input)

    def detect_language(self, text: str):
        '''detect language by text'''
        return classify(text)[0]

    def show_datetime(self):
        '''show date and time'''
        datetime_now = datetime.datetime.now()
        return {'date': datetime_now.strftime('%Y-%m-%d'), 'time': datetime_now.strftime('%H:%M:%S')}

    def say_hello(self):
        '''saying hello and good(Morning/Afternoon/Evening)'''
        hour = datetime.datetime().now()
        if hour >= 0 and hour < 12:
            return "Hello,Good Morning"
        elif hour >= 12 and hour < 18:
            return "Hello,Good Afternoon"
        else:
            return "Hello,Good Evening"

    def search_wikipedia(self,text:str,summary:True,suggestion=False):
        '''search in wikipedia'''
        result = None
        if summary :
            result = wikipedia.summary(text)
        else:
            result = wikipedia.search(text,suggestion=suggestion)
        return result

    def open_website(self, website_url):
        '''opening a website in default browser.(in new tab)'''
        webbrowser.open_new_tab(website_url)
        return f"{website_url} is open"

    def shutdown_system(self):
        '''shutdowning system'''
        os.system('shutdown -h 60')
        return "system will be shutdown in 60 second"

    def cancle_shutdowning_system(self):
        '''cancle shutdowning system'''
        os.system('shutdown -h 60')
        return "system shutdowning cancled"

    def reboot_system(self):
        '''rebooting system'''
        os.sysconf('reboot')

    def search_in_web(self, input):
        '''search in the web by default browser'''
        webbrowser.open_new_tab(input)
        return 'opening browser and searching for result'

    def listen(self):
        '''listen from microphone for get input/command for execute'''
        self.mode = 'listen'
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        audio_text = r.recognize_sphinx(audio)
        detect_audio_lang = self.detect_language(audio_text)
        return (audio_text, audio_text)
        # if internet_on() == True:
        #    print r.recognize_google(audio)
        #    return  r.recognize_google(audio)
        # else:
        #    print r.recognize_sphinx(audio)
        #    return  r.recognize_sphinx(audio)

    def run(self):
        self.__running = True

    def stop(self):
        self.__running = False
