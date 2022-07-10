#!/usr/bin/env python3

import re
import requests
import datetime
import os
import logging
from subprocess import getoutput, getstatusoutput
from platform import system as __os_name
from inspect import getfullargspec
from threading import Thread
from hashlib import sha256
from io import BytesIO
from os import path
from colorama import Fore,Style


import gtts
import webbrowser
import playsound
import utilities
import aiml
import pyttsx3
import wikipedia
import speech_recognition as sr
from googletrans import Translator
from datetime import datetime
from langid import classify
from gtts import gTTS
from jokeapi import Jokes



from modes import Modes
from operations_checkers import Checkers
from operations_input_extractor import OperationInputManipulation

class Emma:

    __instance_count: int = 0

    def __init__(self, brain_file="brain.brn",
                 learn_files=['learn.aiml', ], commands=['LOAD AIML', ],
                 chdir='aiml', save_log=True, log_file_location='/var/log/emma/',
                 logger_lowest_level='DEBUG',use_thread=False) -> None:

        # test
        log_file_location = './log/logfile.txt'
        # region doc string
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
            logger_lowest_level -> the lowest level that logger can log

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
       # endregion

        # Create aiml kernel
        self.__aiml_kernel = aiml.Kernel()
        # Disable verbose mode
        self.__aiml_kernel.verbose(isVerbose=False)

        # bootstraping aiml
        Thread(target=self.__bootstraping_aiml_kernel, args=(
            brain_file, learn_files, commands, chdir)).start()

        # set aiml kernel name
        self.__aiml_kernel.setBotPredicate('name', 'Emma')

        # infity thread
        infity_thread = Thread(target=self.__infity_loop, args=()).start()

        self.__public_functions = [
            m for (m) in dir(Emma) if not m.startswith("_")]

        self.__functions_require_internet = self.__recognize_functions_require_internet(
            self.__public_functions)

        self.__functions_dont_require_internet = self.__recognize_functions_dont_require_internet(
            self.__public_functions, self.__functions_require_internet)

        '''
        In python i can't do something like this:
        string = "blah blah blah   \"
        If backslash be in end of string at least vs code throw "String literal is unterminated"
        My solution is written in below line and in finally maybe just i don't know how do this...
        '''
        self.__backslash = "\ ".strip()


        self.__save_log = save_log
        self.__logger: logging = self.__bootstraping_logger(
            log_file_location)
        self.__use_thread = use_thread
        self.__speak_lang = 'en'
        self.__ping_counter = 0
        self.__number_of_operations_performed = 0
        self.__infity_loop_worked = False
        self.__aiml_kernel_loaded = False
        self.__ping_counter = 0
        self.__running = True
        self.__os_name = __os_name()
        self.__internet_connection: bool = False
        self.__mode: Modes = Modes.ready
        self.__input: dict = {"text": "", "lang": ""}
        self.__output: dict = {"text": "", "lang": self.__speak_lang}

        Emma.__instance_count += 1

    # region private methods
    def __is_need_internet_connection():
        '''decorator for functions needs to internet connection, with this decorator, they can be recognized'''
        def wrapper(func):
            func.need_internet = True
            return func

        return wrapper

    def __bootstraping_logger(self, log_file_location: str):
        log_file_location.strip()
        if log_file_location != '':
            if not path.isdir(path.dirname(log_file_location)):
                os.makedirs(path.dirname(log_file_location), exist_ok=True)

            logging.basicConfig(filename=log_file_location,
                                format='[%(asctime)s] %(name)s: %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
            return logging

    def __bootstraping_aiml_kernel(self, brainFile, learnFiles, commands, chdir):
        '''load aiml brain, if not exist load learn files. (bootstraping aiml kernel'''

        # load brain file if exist
        brain_path = chdir + "/" + brainFile
        if path.isfile(brain_path):
            self.__aiml_kernel.loadBrain(brain_path)
        elif path.isfile(chdir + brainFile):
            self.__aiml_kernel.loadBrain(chdir+brainFile)

        # brain file not exist, so load learn files. it takes more time than load brain, brain file is binary file
        else:
            self.__aiml_kernel.bootstrap(
                learnFiles=learnFiles, commands=commands, chdir=chdir)
            self.__aiml_kernel.saveBrain("aiml/brain.brn")
        self.__aiml_kernel_loaded = True

    def __recognize_functions_require_internet(self, all_functions_name: list):
        functions_need_internet: list = []
        for f in all_functions_name:
            command = f"self.{f}.need_internet"

            try:
                result = eval(command)
            except:
                continue

            if result == True:
                functions_need_internet.append(f)

        return functions_need_internet

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

    def __recognize_functions_dont_require_internet(self, all_functions_name: list, functions_require_internet: list):
        functions_dont_require_internet = [
            f for f in all_functions_name if f not in functions_require_internet]
        return functions_dont_require_internet

    def __check_internet_connection(self):
        '''internet connection checking'''

        status = True
        g_ping = os.system('ping -c 1 google.com > /dev/null 2>&1')
        if g_ping != 0:
            y_ping = os.system('ping -c 1 yahoo.com > /dev/null 2>&1')
            if y_ping != 0:
                g_dns = os.system('ping -c 1 8.8.8.8 > /dev/null 2>&1')
                if g_dns != 0:
                    status = False

        self.__internet_connection = status
    
    def __infity_loop(self):
        '''this mehtod is a loop for check things (like internet connection)'''
        while 1:
            self.__check_internet_connection()
            self.__ping_counter += 1
            if self.__ping_counter == 1:
                self.__infity_loop_worked = True

            # when uncomment these lines i get error with text: IO was closed or something like that
            # if KeyboardInterrupt:
            #     exit()

    # endregion

    # region public methods

    def tell_joke(self,language='',category:str=''):
        joke = ''
        
        j =  Jokes()
        if category != '':
            data = j.get_joke(category=[category,],lang=language)
        else:
            data = j.get_joke(lang=language)
        if data['error'] == False:
            try:
                joke = data['joke']
            except:
                joke = data['setup'] + '\n'
                joke += data['delivery']
        else:
            return data['message']
        
        return joke
        

    @classmethod
    def instance_count(cls):
        return f"Instance count is {cls.__instance_count}"

    def run(self):
        self.__mode = Modes.ready
        self.__running = True
        return "Now, I'm running"

    def stop(self):
        self.__mode = Modes.stopped
        self.__running = False
        return "Now,I'm stopped"

    def public_operations(self):
        '''all public operations'''
        return [item for item in self.__public_functions]

    def user_operations(self):
        '''return all public operations with a little rename for user undrestanding'''
        operations = self.public_operations

        remove_operations = ('speak_gtts', 'speak_pyttsx3', 'translate_google')

        add_operations = ('speak', 'translate')

        # Remove some operations
        for op in remove_operations:
            try:
                operations.remove(op)
            except:
                continue

        # Add some operations
        for op in add_operations:
            try:
                operations.append(op)
            except:
                continue

        operations = [op.replace("_", " ").capitalize() for op in operations]
        return operations

    def internet_connection_status(self):
        '''show internet connection status'''
        if self.__internet_connection == True:
            return "You're connect to the internet"
        else:
            return "No internet connection"

    def command_mode(self):
        '''set mode to command'''
        if self.__os_name == "Linux":
            self.__mode = Modes.command
            return "You are in command mode now."
        else:
            return "This Operation can just run in linux operation system, for now"

    def run_command(self, command):
        '''runs a command in shell and returns the output'''
        if command:
            exit_code, output = getstatusoutput(command)
            return output + f"\nExit code:{exit_code}"
        else:
            return "The command input is empty."

    def change_speaking_language(self, language: str):
        ''''''
        if not language.strip() == '':

            def convert_language_to_language_code(language):
                return utilities.get_key_by_value(
                    language, supported_languages_dict)

            lowered_language = language.lower()
            capitalized_language = language.capitalize()
            del language

            # Support languages with their code in a dict
            supported_languages_dict = gtts.tts.tts_langs()
            # Languages | All languages are capitalized
            supported_languages = list(supported_languages_dict.values())
            # Languages code | All languages code are lowered(lower case)
            supported_languages_codes = list(supported_languages_dict.keys())

            if lowered_language not in supported_languages_codes and capitalized_language not in supported_languages:
                return "Can't change language,please check grammer of your language.\nYou can enter both language name and language code.\nFor Example:\n\tenglish or en\n\tfrench or fr"

            # Convert language to language code
            # Like 'english' to 'en' or 'french' to 'fr'
            # if language convertable to language code, put it into lowered_language variable
            if capitalized_language in supported_languages:
                lowered_language = convert_language_to_language_code(
                    capitalized_language)

            # Put language name in capitalized_language
            capitalized_language = supported_languages_dict[lowered_language].capitalize(
            )

            # Check that the input language and currently language ​​are same
            if lowered_language == self.__speak_lang:
                return f"I'm currently speak in {capitalized_language}"

            # Now we have language code in lowered_language variable and we can change Emma language
            if lowered_language in supported_languages_codes:
                self.__speak_lang = lowered_language
                self.__output['lang'] = self.__speak_lang
                return f'Speak language changed to {capitalized_language}.'

    def speak_gtts(self, text: str, lang: str):
        '''speak by google text to speech service/api (online)'''

        '''Google support only 100 character in a request.\
        so we need to send some request if text has more than 100 character'''
        if len(text) < 1:
            raise Exception('text parameter is empty')

        filename = sha256(str(text + lang).encode()).hexdigest()

        # Path of file for save it, file name is sha256 of text and lang
        path = f'./voices/{filename}.mp3'
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

        # Play voice
        playsound.playsound(path)

    def speak_pyttsx3(self, text: str):
        '''speak by pyttx3 service (offline)'''
        try:
            pyttsx3_engine = pyttsx3.init()
            pyttsx3_engine.setProperty('rate', 145)
            pyttsx3_engine.say(text)
            pyttsx3_engine.runAndWait()
        except:
            if self.__os_name == "Linux":
                os.system('sudo apt install espeak')
            elif self.__os_name == "Windows":
                print("Sorry, I can't speak because you are not connect to the internet.\nIf you want i can speak without internet connection please install \"espeak\" that help me to talk to you when you are offline.")

    @__is_need_internet_connection()
    def translate_google(self, text: str, dest_lang: str = 'en'):
        '''translate a text with google translation service/api (online)'''
        t = Translator()
        return t.translate(text, dest_lang).text

    def ping_counter(self):
        return f"I have pinged {self.__ping_counter} times so far."

    def ping(self, server):
        output = getoutput(f'ping -c 1 {server}')
        return output

    def aiml_response(self, input):
        '''get aiml response by a input'''

        # If aiml not loaded print a waiting messages
        if self.__aiml_kernel_loaded == False:
            print("\nPlease wait few soconds to load aiml kernel")

        # Wait to load aiml kernel
        while self.__aiml_kernel_loaded == False:
            pass

        return self.__aiml_kernel.respond(input)

    @__is_need_internet_connection()
    def say_quote(self,author='', genre='', limit=1, all_quotes=False, all_authors=False):
        '''
        Return a quote by parameter.
        Parameter:
            author -> is someone who wrote the quote
            genre -> is genre of quote like: war,age,politics
            limit -> is limit of quotes
            all_qoutes -> if be true all quotes will return
            all_authors -> if be true all authors will return
        Returns:
            A string of quotes or authors
        '''
        base_url = 'https://quote-garden.herokuapp.com/api/v3/'
        result = ''
        number_quotes = 0
        number_authors = 0

        def get_quotes(url):
            '''
            Get quotes
            Returns:
            A tuple of quotes and number of quotes'''
            result = [{'quote': '', 'author': ''}]
            # Number of pages with quotes
            total_pages = 0
            # Get total pages
            total_pages = int(requests.get(url).json()[
                              'pagination']['totalPages'])

            # Get pages from 1 to total_pages
            for page_number in range(1, total_pages+1):
                if '?' in url:
                    response = requests.get(url+f'&page={page_number}').json()
                else:
                    response = requests.get(url+f'?page={page_number}').json()
                if response['statusCode'] != 200:
                    continue
                if response['data'] == '':
                    break
                for quotes_number in range(0, len(response['data'])):
                    quote = response['data'][quotes_number]['quoteText']
                    author = response['data'][quotes_number]['quoteAuthor']
                    result.append({'quote': quote, 'author': author})

            # Pretty result
            if len(result) > 0:
                pretty_result = ""
                # First element is empty. see declaration of result variable, so i'm skip that element
                for n in range(1, len(result)):
                    quote = result[n]['quote']
                    author = result[n]['author']
                    pretty_result = pretty_result + \
                        f'"{quote}"\n--- {author}\n\n'

            return (pretty_result, len(result))

        def get_all_authors():
            '''
            Returns all authors
            Returns:
            A tuple of authors and number of authors'''
            authors = ''
            number_authors = 0
            response = requests.get(base_url+'authors').json()

            for author in response['data']:
                if author.strip() == '':
                    continue
                authors = authors + f"{author}\n"
                number_authors = number_authors + 1
            return (authors, number_authors)

        # region If all_quotes or all_authors were True
        if all_quotes:
            quotes, number_quotes = get_quotes(url=base_url+'quotes')
            result = quotes + f"\n\nNumber of Quotes: {number_quotes}"

        if all_authors:
            result, number_authors = get_all_authors()
            result = result + f"\n\nNumber of Authors: {number_authors}"

        if all_authors == True or all_quotes == True:
            return result
        # endregion

        # If all_quotes or all_authors were False
        full_url = base_url + 'quotes?'
        if author != '':
            full_url = full_url + f'author={author}&'
        if genre != '':
            full_url = full_url + f'genre={genre}'
        full_url += f'&limit={limit}'
        result, number_quotes = get_quotes(full_url)

        # Add number of quotes in result
        result = result + f"\n\nNumber of Quotes: {number_quotes}"
        return result

    def detect_language(self, text: str):
        '''detect language by text'''
        return classify(text)[0]

    def show_datetime(self, time=True, date=True):
        '''show date and time'''
        datetime_now = datetime.now()
        result = ''
        if time:
            time = datetime_now.strftime('%H:%M:%S')
            result = result + f"\nTime is : {time}.\n"
        if date:
            date = datetime_now.strftime('%Y-%m-%d')
            result = result + f"Date is : {date}."

        return f"{result}"

    def say_hello(self):
        '''saying hello and good(Morning/Afternoon/Evening)'''
        hour = datetime.now().hour
        if hour >= 0 and hour < 12:
            return "Hello, Good Morning"
        elif hour >= 12 and hour < 18:
            return "Hello, Good Afternoon"
        else:
            return "Hello, Good Evening"

    @__is_need_internet_connection()
    def search_in_wikipedia(self, text: str, summary: True):
        '''search in wikipedia'''
        result = None
        if summary:
            result = wikipedia.summary(text)
        else:
            result = wikipedia.page(text).content
        return result

    @__is_need_internet_connection()
    def open_website(self, website_url):
        '''opening a website in default browser.(in new tab)'''
        webbrowser.open_new_tab(website_url)
        return f"{website_url} is open"

    def shutdown_system(self):
        '''shutdowning system'''
        if self.__os_name == "Linux":
            os.system('shutdown -h 60')
        elif self.__os_name == "Windows":
            os.system("shutdown /s /t 60")
        else:
            return "i don't support this operating system"

        return "system will be shutdown in 60 seconds"

    def create_directory(self, name: str, location: str):
        result = False

        # putting slash or backslash in location if there is not
        if not location == '':
            if not location.endswith('/') or not location.endswith(self.__backslash):
                if self.__os_name == "Linux":
                    if not location.endswith('/'):
                        location = location + "/"
                elif self.__os_name == "Windows":
                    if not location.endswith(self.__backslash):
                        location = location + self.__backslash

        if name:
            if location:
                if self.__os_name == "Linux" or self.__os_name == "Windows":
                    result = True if os.system(
                        f"mkdir {location+name}") == 0 else False
            else:
                if self.__os_name == "Linux" or self.__os_name == "Windows":
                    result = True if os.system(f"mkdir {name}") == 0 else False

        if result:
            return "directory successfully created"
        else:
            return "directory not created"

    def cancel_shutdowning_system(self):
        '''cancel shutdowning system'''
        if self.__os_name == "Linux":
            os.system('shutdown -c')
        elif self.__os_name == "Windows":
            os.system('shutdown -a')
        else:
            return "i don't support this operating system"

        return "system shutdowning canceled"

    def reboot_system(self):
        '''rebooting system'''
        if self.__os_name == "Linux":
            os.system('shutdown -r 60')
        elif self.__os_name == "Windows":
            os.system("shutdown -r -f -t 60 ")

        return "system will be reboot in 60 second"

    @__is_need_internet_connection()
    def search_in_web(self, input):
        '''search in the web by default browser'''
        webbrowser.open_new_tab(f'https://www.google.com/search?q={input}')
        return 'opening browser and searching for result'

    def listen(self):
        '''listen from microphone for get input/command for execute'''
        self.__mode = Modes.listening

        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)

        if self.__internet_connection:
            audio_text = r.recognize_google(audio)
        else:
            audio_text = r.recognize_sphinx(audio)

        detect_audio_lang = self.detect_language(audio_text)
        return (audio_text, detect_audio_lang)

    def mode(self):
        '''returns mode of Emma'''
        return self.__mode.name.capitalize()

    def __input_processing(self, input):
        '''Processing input and detect operation'''
        operation = None
        operation_inputs = None
        operation_name = None

        # For on all checkers
        for checker in Checkers.all_public_checkers():
            checker_result = eval(f"Checkers.{checker}(\"{input}\")")

            # If checker returns True result
            if checker_result == True:
                # remove checker word from checker function and then we have operation name
                operation_name = checker[:-8]
                operation = eval(f"self.{operation_name}")
                operation_parameter_count = len(getfullargspec(operation).args)

                # If parameters/inputs count more than 1, so should extract input and send to the operation/function
                if operation_parameter_count > 1:
                    # Extract input for operation/function
                    input_manipulation_func = OperationInputManipulation.get_input_manipulator_by_operation_name(
                        operation_name)
                    operation_inputs = input_manipulation_func(input)
                break
        else:
            if not operation and not operation_name:
                operation_name = 'aiml_response'
                operation = eval(f"self.aiml_response")
                operation_inputs = input

        result: dict = {
            "operation": operation,
            'operation_inputs': operation_inputs,
            "require_internet": True if operation_name in self.__functions_require_internet else False
        }

        return result

    def __perform_operation(self, operation_attributes: dict):
        '''
        Perform an operation
        operation_attributes -> is a dict[operation,operation_inputs,require_internet]
        '''

        # if operation needs internet connection, so should tell user
        if operation_attributes["require_internet"]:
            if self.__internet_connection == False:
                self.__output['text'] = "This operation require internet connection,If you would like to do this operation, please connect to the internet."

        # fill self.__output['text']
        if self.__output['text'] == '':
            operation_inputs = operation_attributes['operation_inputs']
            operation = operation_attributes['operation']

            # clean up memory
            del operation_attributes

            if type(operation_inputs) == dict:
                # Fill Emma speak language, if selected
                if 'lang' in operation_inputs.keys():
                    for lang, lang_code in gtts.tts.tts_langs().items():
                        if operation_inputs['lang'] == lang or operation_inputs['lang'] == lang_code:
                            self.__output['lang'] = operation_inputs['lang']
                    del operation_inputs['lang']
                else:
                    if self.__output['lang'] != self.__speak_lang:
                        self.__output['lang'] = self.__speak_lang
                # try:
                #     for lang, lang_code in gtts.tts.tts_langs().items():
                #         if operation_inputs['lang'] == lang or operation_inputs['lang'] == lang_code:
                #             self.__output['lang'] = operation_inputs['lang']

                #     del operation_inputs['lang']
                # except:
                #     self.__output['lang'] = self.__speak_lang

                # Execute operation with arguments/inputs
                self.__output['text'] = operation(**operation_inputs)
            else:
                if operation_inputs == None:
                    self.__output['text'] = operation()
                else:
                    self.__output['text'] = operation(operation_inputs)

    def __output_processing(self):
        # Capitalize
        output_text = utilities.upper_first_letter(
            str(self.__output['text'])) if len(str(self.__output['text'])) > 0 else ''
        output_lang = self.__output['lang']
        # Print output
        print("Emma : " + output_text)
        # If output not empty and nonsense
        if output_text.strip() != '' and re.sub('[^\w]', '', output_text.strip()) != '':

            # All previously saved voice
            saved_voices_name = getoutput('ls ./voices/').splitlines()

            # The name of the voice files is sha256 their text and language code (with .mp3)
            # sha256 of output text and output lang
            output_sha256 = sha256(
                str(output_text+output_lang).encode()).hexdigest()

            output_filename = f'{output_sha256}.mp3'

            if output_filename in saved_voices_name:
                playsound.playsound(f'./voices/{output_sha256}.mp3')
            elif self.__internet_connection:
                self.speak_gtts(output_text, self.__output['lang'])
            else:
                self.speak_pyttsx3(output_text)

    def __after_processing(self):
        '''Doing some work after operation processing(clean up,logging,etc...)'''

        # Logging Informations
        msg = f"\nInput: {self.__input['text']}\nOutput: {self.__output['text']}"
        self.__log(msg, level='INFO')

        # Clean up
        self.__output['text'] = ''
        self.__output['lang'] = self.__speak_lang

    def __command_mode_processing(self):
        '''Processing command mode stuff'''
        while True:
            # Get user name and device name and current directory (pwd)
            user_name = getoutput('whoami')
            device_name = getoutput('hostname')
            pwd = getoutput('pwd')
            
            # Colored shell symbols and in the end of string reset color to normal
            shell_symbols = f"{Fore.LIGHTGREEN_EX}{user_name}@{device_name}:{Fore.LIGHTBLUE_EX}{pwd}{Style.RESET_ALL}$ "
            
            # Get command
            cmd = input(shell_symbols)


            out_words = ('come out from command mode',
                         'go to normal mode', 'goto normal mode')
            if cmd in out_words:
                self.__mode = Modes.ready
                self.__output['text'] = "You are out of commnad mode"
                self.__output_processing()
                self.__after_processing()
                break
            self.__output['text'] = self.run_command(cmd)
            self.__output_processing()
            self.__after_processing()

    def __ready_mode_processing(self):
        '''
        Processing ready mode stuff.
        This method needs self.input['text'] as input, so that variable should been fill.
        '''
        self.__mode = Modes.processing

        # Input processing ----- select appropriate operation and extract required inputs
        # operaion_attributes has "operation,operation_inputs,required_internet"
        operation_attributes = self.__input_processing(
            self.__input['text'])

        # Wait for check internet connection done at least, one time
        while self.__infity_loop_worked == False:
            pass

        # Perform selected operation
        self.__perform_operation(operation_attributes)

        # Output processing
        self.__output_processing()

        # Cleaning and logging,etc
        self.__after_processing()
        if self.__mode != Modes.command:
            self.__mode = Modes.ready

    def __stop_mode_processing(self):
        # If user want to start Emma
        if Checkers.run_checker(self.__input['text']):
            self.__output['text'] = self.run()
        # Tell user i stopped
        else:
            self.__output['text'] = "I'm stopped, please first run me.\nYou can do it by say \"Run\". "
        # Process stop mode output
        self.__output_processing()
        

    def processing(self):
        '''Input processing and performing the input request and display the final output'''
        
        if self.__mode != Modes.stopped:
            # Command mode
            if self.__mode == Modes.command:
                self.__command_mode_processing()
            # Ready mode
            elif self.__mode == Modes.ready:
                # Get text input
                self.__input['text'] = input('You: ')
                # Get audio input
                #self.__input['text'],self.__input['lang'] = self.listen()
                self.__ready_mode_processing()
        # Stop mode
        else:
            # Get input
            self.__input['text'] = input('You: ')
            self.__stop_mode_processing()


emma = Emma()

while(1):
    emma.processing()
