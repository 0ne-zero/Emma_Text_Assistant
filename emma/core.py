#!/usr/bin/env python3
from io import BytesIO
import logging
from os import path, makedirs, system
import re
from subprocess import getoutput
from time import sleep
import aiml
import speech_recognition as sr
import logging
from threading import Thread
import aiml
import pyttsx3

import operation
from globals import GET_GLOBAL_VARS
import state
import utilities
from gtts import gTTS
from playsound import playsound
from state import IState, TextState


class Core():
    def __init__(self, default_state,brain_file,
                 learn_files, commands,
                 chdir, save_log, log_file_location,
                 log_level, use_thread, versobe) -> None:
        '''
        Parameter:
            brain_file -> is binary file to load aiml kernel. (default location = /aiml/brain.brn)
            learn_files -> are files which load aiml kernel. (default location = /aiml/learn.aiml)
            commands -> are commands which run in leran files. (default is "LOAD AIML")
            chdir -> is a path which before load aiml files or brain, change to that path,
            If your learn file or brain file is in default location use chdir to say folder location.

            default_shell -> address of that shell you use. (default is "/usr/bin/sh")

            save_log -> if be True the Emma class logger will be enable
            log_file_location -> path to save log file
            log_level -> the lowest level that logger can log

            Example:
            Directory tree:
            /some_folder/another_folder/aiml_learn_file.aiml
            /some_folder/another_folder/another_learn_file.aiml
            /some_folder/another_folder/aiml_brain_file.brn

            In above example you argument should be like this:
            brain_file = "aiml_brain_file.brn"
            learn_files = ["aiml_learn_file.aiml","another_learn_file.aiml"]
            chdir = "some_folder/another_folder/

            If your directory tree is default,it meens like this:
            /aiml/brain.brn
            /aiml/learn_files.aiml

            As you can see there are default parameter, so you don't need to send arguments to this method...

            *If you don't have custom learn file or brain file, leave brain_file,learn_files,commands,chdir arguments alone.
        '''

        log_file_location = './log/logfile.txt'

        # Create aiml kernel
        __aiml_kernel = aiml.Kernel()
        # Disable verbose mode
        __aiml_kernel.verbose(isVerbose=False)
        # Set aiml kernel name
        __aiml_kernel.setBotPredicate('name', 'Emma')

        GET_GLOBAL_VARS().set("__aiml_kernel", __aiml_kernel)

        '''
        In python i can't do something like this:
        string = "blah blah blah   \"
        If backslash be in end of string at least vs code throw "String literal is unterminated"
        My solution is written in below line and in finally maybe just i don't know how do this...
        '''
        GET_GLOBAL_VARS().set('__backslash', '\ '.strip())

        # bootstraping aiml
        if use_thread:
            Thread(target=self.__bootstraping_aiml_kernel, args=(
                brain_file, learn_files, commands, chdir)).start()
        else:
            self.__bootstraping_aiml_kernel(
                brain_file, learn_files, commands, chdir)

        # Infity thread
        Thread(target=self.__infity_loop, args=()).start()

        GET_GLOBAL_VARS().set('__using_thread', use_thread)
        GET_GLOBAL_VARS().set('__verbose', versobe)

        # bootstrap logger
        self.__logger: logging = self.__bootstraping_logger(
            log_file_location)

        self.speak_lang = 'en'
        self.ping_counter = 0
        self.number_of_operations_performed = 0
        self.infity_loop_worked = False
        self.aiml_kernel_loaded = False
        self.is_state_changed = False
        self.ping_counter = 0
        self.running = True
        # They aren't private because states need them
        self.state = default_state
        self.input: dict = {"text": "", "lang": ""}
        self.output: dict = {"text": "", "lang": self.speak_lang}

    # region private methods

    def __bootstraping_logger(self, log_file_location: str):
        log_file_location.strip()
        if log_file_location != '':
            if not path.isdir(path.dirname(log_file_location)):
                makedirs(path.dirname(log_file_location), exist_ok=True)

            logging.basicConfig(filename=log_file_location,
                                format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            return logging

    def __bootstraping_aiml_kernel(self, brainFile, learnFiles, commands, chdir):
        '''load aiml brain, if not exist load learn files. (bootstraping aiml kerne)'''
        # get aiml kernel
        kernel = GET_GLOBAL_VARS().get("__aiml_kernel")

        # load brain file if exist
        brain_path = chdir + "/" + brainFile
        if path.isfile(brain_path):
            kernel.loadBrain(brain_path)
        elif path.isfile(chdir + brainFile):
            kernel.loadBrain(chdir+brainFile)

        # brain file not exist, so load learn files. it takes more time than load brain, brain file is binary file
        else:
            kernel.bootstrap(
                learnFiles=learnFiles, commands=commands, chdir=chdir)
            kernel.saveBrain("aiml/brain.brn")
        GET_GLOBAL_VARS().set('__is_aiml_kernel_loaded', True)

    def __log(self, msg: str, level: str):
        try:
            if msg:
                if not level.isupper():
                    level = level.upper()
            if level == 'DEBUG':
                self.__logger.debug(msg)
            elif level == 'INFO':
                self.__logger.info(msg)
            elif level == 'WARNING':
                self.__logger.warning(msg)
            elif level == 'ERROR':
                self.__logger.error(msg)
            elif level == 'CRITICAL':
                self.__logger.critical(msg)
                return True
        except:
            return False

    def __check_internet_connection(self):
        '''internet connection checking'''

        status = True
        g_ping = system('ping -c 1 google.com > /dev/null 2>&1')
        if g_ping != 0:
            y_ping = system('ping -c 1 yahoo.com > /dev/null 2>&1')
            if y_ping != 0:
                g_dns = system('ping -c 1 8.8.8.8 > /dev/null 2>&1')
                if g_dns != 0:
                    status = False

        GET_GLOBAL_VARS().set('__internet_connection', status)

    def __infity_loop(self):
        '''this mehtod is a loop for check things (like internet connection)'''
        while 1:
            self.__check_internet_connection()
            self.ping_counter += 1
            if self.ping_counter == 1:
                self.infity_loop_worked = True
            sleep(0.4)

    def __speak_gtts(self, text: str, lang: str):
        '''Get audio from google text to speech api and save it in local disk and play it'''

        '''Google support only 100 character in a request.\
        so we need to send some request if text has more than 100 character'''
        if len(text) < 1:
            raise Exception('text parameter is empty')

        filename = utilities.generate_hash_sha256(text, lang)

        # Path of file for save it, file name is sha256 of text and lang
        path = f'./audios/{filename}.mp3'
        del filename

        if len(text) > 100:
            # Slice text into pieces (list)
            sentences = utilities.smalling_text(text, 100)

            # Download many mp3 files and save them in memroy and then save them all in one file on disk.
            bytes = bytearray()

            for sentence in sentences:
                # Download and store in memory
                gtts = gTTS(sentence, lang=lang)
                mem_file = BytesIO()
                gtts.write_to_fp(mem_file)

                # Append bytes
                bytes += bytearray(mem_file.getvalue())
            with open(path, 'wb') as file:
                file.write(bytes)
        else:
            gtts = gTTS(text, lang=lang)
            gtts.save(path)

        # Play audio
        playsound(path)

    def __speak_pyttsx3(self, text: str):
        '''speak by pyttx3 service (offline)'''
        try:
            pyttsx3_engine = pyttsx3.init()
            pyttsx3_engine.setProperty('rate', 145)
            pyttsx3_engine.say(text)
            pyttsx3_engine.runAndWait()
        except:
            if self.__os_name == "Linux":
                system('sudo apt install espeak | yes')
            elif self.__os_name == "Windows":
                print("Sorry, I can't speak because you are not connect to the internet.\nIf you want i can speak without internet connection please install \"espeak\" that help me to talk to you when you are offline.")

    # endregion

    # region public methods

    def listen(self):
        '''listen from microphone for get input/command for execute'''
        r = sr.Recognizer()

        with sr.Microphone(sample_rate=48000, chunk_size=1024) as source:
            r.adjust_for_ambient_noise(source, duration=3)
            print("I'm listening...")
            audio = r.listen(source)

        if GET_GLOBAL_VARS().get('__internet_connection'):
            audio_text = r.recognize_google(audio)
        else:
            audio_text = r.recognize_sphinx(audio)

        op = operation.DetectLanguage()
        op.input_extractor(audio_text)
        detect_audio_lang = op.action()

        return (audio_text, detect_audio_lang)

    @classmethod
    def instance_count(cls):
        return f"Instance count is {cls.__instance_count}"

    def print_output(self) -> None:
        '''Prints output in screen'''
        # Capitalize
        output_text = utilities.upper_first_letter(
            str(self.output['text'])) if len(str(self.output['text'])) > 0 else ''
        # Print output
        print("Emma : " + output_text)

    def say_output(self) -> None:
        '''This method play audio in speaker (speaks)'''

        # Capitalize
        output_text = utilities.upper_first_letter(
            str(self.output['text'])) if len(str(self.output['text'])) > 0 else ''
        output_lang = self.output['lang']
        # If output not empty and nonsense

        if output_text.strip() != '' and re.sub('[^\w]', '', output_text.strip()) != '':
            # All previously saved audio
            saved_audios_name = getoutput('ls ./audios/').splitlines()

            # The name of the audio files is sha256 their text and language code (with .mp3)
            # sha256 of output text and output lang
            output_sha256 = utilities.generate_hash_sha256(
                output_text, output_lang)

            output_filename = f'{output_sha256}.mp3'

            # If output audio already saved in previous audios
            if output_filename in saved_audios_name:
                # We play it from local
                playsound(f'./audios/{output_sha256}.mp3')
            else:
                # If there is internet connection
                if GET_GLOBAL_VARS().get('__internet_connection'):
                    # Get output audio from google text to speech
                    self.__speak_gtts(output_text, output_lang)
                else:
                    self.__speak_pyttsx3(output_text)
    
    def log(self,msg,log_level="INFO"):
        pass
   
    def processing(self):
        # It's true just for going to while loop
        # If current state changes state it set self.is_state_changed true otherwise doesn't do anything
        self.state.processing(self)
