from abc import ABC, abstractmethod
import ast
import datetime
import os
from platform import platform
from time import sleep
from subprocess import getoutput
import webbrowser

import requests
import datetime
import os
from subprocess import getoutput, getstatusoutput
from gtts.tts import tts_langs
import webbrowser

import wikipedia
from googletrans import Translator
from datetime import datetime
from langid import classify
from jokeapi import Jokes

from globals import GET_GLOBAL_VARS

INITIATED = False

def __all_operations():
    parsed = ast.parse(open(__file__).read())
    # all operations are class
    classes = [c for c in parsed.body if isinstance(c,ast.ClassDef)]
    operations_class = []
    for c in classes:
        if c.bases[0].id == "IOperation":
            operations_class.append(
                globals()[c.name]
            )
    return operations_class
def __needs_internet_connection(cls):
    '''decorator for functions needs to internet connection, with this decorator, they can be recognized'''
    cls.need_internet = True
    return cls


def __needs_input(cls):
    '''decorator for functions needs to input for their action'''
    cls.need_input = True
    return cls

class IOperation(ABC):
    @abstractmethod
    def checker(input):
        '''this should be a static method'''
        pass

    @abstractmethod
    def action(self):
        # validate conditions for running action
        # if there is something unvalidate raise an error
        self.__before_action_validate()

    @abstractmethod
    def input_extractor(self, input):
        pass

    def __is_input_extracted(self):
        if not hasattr(self, 'input_extracted'):
            return False
        return self.input_extracted

    def _set_input_extracted_true(self):
        self.input_extracted = True

    def __before_action_validate(self):
        if hasattr(type(self),'need_input'):
            if type(self).need_input == True:
                if not self.__is_input_extracted():
                    raise Exception("You should call input_extractor before action")

@__needs_input
class AIMLResponse(IOperation):
    def action(self):
        '''get aiml response by a input'''
        super().action()

        # If aiml not loaded print a waiting messages
        is_kerenl_laoded = GET_GLOBAL_VARS().get('__is_aiml_kernel_loaded')
        # Get is_kernel_loaded till it's don't be None (None means doesn't exists, atleast yet)
        while is_kerenl_laoded == None:
            is_kerenl_laoded = GET_GLOBAL_VARS().get('__is_aiml_kernel_loaded')
            sleep(0.2)
        if is_kerenl_laoded == False:
            print("\nPlease wait few soconds to load aiml kernel")
        # Wait to load aiml kernel
        while is_kerenl_laoded == False:
            sleep(0.2)
            
        kernel = GET_GLOBAL_VARS().get("__aiml_kernel")

        return kernel.respond(self.text)
    @staticmethod
    def checker(input):
        # this is a special operation if rest of operations checker returns False this operation will be call by force
        return False
    def input_extractor(self, input):
        self.text = input
        self._set_input_extracted_true()
@__needs_internet_connection
@__needs_input
class OpenWebsite(IOperation):
    @staticmethod
    def checker(input):
        open_website_keywords = ('open', 'browse', 'google')
        for item in open_website_keywords:
            if input.startswith(item) and input.endswith('website'):
                return True
        return False

    def action(self):
        '''opening a website in default browser.(in new tab)'''
        # run base class action first
        super().action()
        webbrowser.open_new_tab(self.website_url)
        return f"{self.website_url} is open"

    def input_extractor(self, input):
        additionals_start = ('browse', 'search', 'google')
        input = input.replace('website', '')
        for additional in additionals_start:
            if input.startswith(additional):
                input = input.replace(additional, '')

        self.website_url = input.strip()

        self._set_input_extracted_true()


class ShutDownSystem(IOperation):
    def action(self):
        '''shutdowning system'''
        super().action()
        if self.__os_name == "Linux":
            os.system('shutdown -h 60')
        elif self.__os_name == "Windows":
            os.system("shutdown /s /t 60")
        else:
            return "i don't support this operating system"

        return "system will be shutdown in 60 seconds"

    def input_extractor(self, input):
        self._set_input_extracted_true()

    @staticmethod
    def checker(input):
        shutdown_system_keywords = (
            'shutdown', 'shutdown system', 'halt system')
        for item in shutdown_system_keywords:
            if input == item:
                return True
        return False


@__needs_input
class CreateDirectory(IOperation):
    def action(self):
        super().action()

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

        if self.name:
            if location:
                if self.__os_name == "Linux" or self.__os_name == "Windows":
                    result = True if os.system(
                        f"mkdir {self.location+self.name}") == 0 else False
            else:
                if self.__os_name == "Linux" or self.__os_name == "Windows":
                    result = True if os.system(
                        f"mkdir {self.name}") == 0 else False

        if result:
            return "directory successfully created"
        else:
            return "directory not created"

    def input_extractor(self, input):
        # for return (for main method)
        inputs = {'name': '', 'location': ''}
        # detect location of directory
        location_words = input.rsplit(" in ", 1)[1].split()

        # if user didn't give directory location this variable will be True
        location_is_here = False

        if len(location_words) > 0:
            if len(location_words) == 1:
                if location_words[0] == 'here' or location_words[0] == 'Here':
                    location_is_here = True
            if location_is_here == False:
                if platform() == "Linux":
                    # ls /
                    root_directories = getoutput('ls /').splitlines()

                    if location_words[0] in root_directories:
                        location_words[0] = f"/{location_words[0]}"

                    # filling inputs['location']
                    counter = 0
                    for word in location_words:
                        if counter == 0:
                            inputs['location'] += word
                        else:
                            inputs['location'] += f"/{word}"
                        counter += 1
                elif platform() == "Windows":
                    # get drives
                    drives_list = getoutput(
                        'wmic logicaldisk get name').splitlines()

                    # if "Name" is in the output, remove it
                    # and remove ":" character from all input
                    for i in range(0, len(drives_list)):
                        # remove ":"
                        drives_list[i] = drives_list[i].replace(
                            ':', '').strip()
                        # remove "Name"
                        if drives_list[i] == "Name":
                            del drives_list[i]
                    # putting \ in end of the first element of location_words
                    if location_words[0].upper() in drives_list:
                        location_words[0] = f'{location_words[0]}:\ '.strip()

                    # filling inputs['location']
                    counter = 0
                    for word in location_words:
                        if counter == 0:
                            inputs['location'] += word
                        else:
                            inputs['location'] += f"{word}\ ".strip()
                        counter += 1

        # detect directory name
        additional_start_words = ("create directory", "create folder")
        for item in additional_start_words:
            input = input.replace(item, '').strip()
        inputs['name'] = input.split(' ', 1)[0]

        self.name = inputs['name']
        self.location = inputs['location']

        self._set_input_extracted_true()

    @staticmethod
    def checker(input):
        create_directory_keywords = ("create directory", "create folder")
        for item in create_directory_keywords:
            if input.startswith(item):
                return True
        return False


class CancleShutdownSystem(IOperation):
    def action(self):
        '''cancel shutdowning system'''
        super().action()
        if self.__os_name == "Linux":
            os.system('shutdown -c')
        elif self.__os_name == "Windows":
            os.system('shutdown -a')
        else:
            return "i don't support this operating system"

        return "system shutdowning canceled"

    @staticmethod
    def checker(input):
        cancle_shutdowning_keywords = (
            'cancel shutdown', 'cancle shutdowning', 'cancel shutdown system')
        for item in cancle_shutdowning_keywords:
            if input == item:
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


class GetOperatingSystemName(IOperation):
    def action(self):
        ''' Returns device os name'''
        super().action()
        return platform.system()

    def checker(input):
        get_os_name_keywords = ('get os name', 'get operating system name')
        for item in get_os_name_keywords:
            if input == item:
                return True

        return False

    def input_extractor(self):
        self._set_input_extracted_true()


class RebootSystem(IOperation):
    def action(self):
        '''rebooting system'''
        super().action()
        if self.__os_name == "Linux":
            os.system('shutdown -r 60')
        elif self.__os_name == "Windows":
            os.system("shutdown -r -f -t 60 ")

        return "system will be reboot in 60 second"

    def checker(input):
        reboot_system_keywords = ('reboot', 'reboot system')
        for item in reboot_system_keywords:
            if input == item:
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


@__needs_input
@__needs_internet_connection
class SayJoke(IOperation):
    def action(self):
        super().action()
        joke = ''

        j = Jokes()
        if self.category != '':
            data = j.get_joke(category=[self.category, ], lang=self.language)
        else:
            data = j.get_joke(lang=self.language)
        if data['error'] == False:
            try:
                joke = data['joke']
            except:
                joke = data['setup'] + '\n'
                joke += data['delivery']
        else:
            return data['message']

        return joke

    def checker(input):
        say_joke_keywords = ('tell me a joke', 'tell me joke',
                             'tell joke', 'tell a joke', 'say a joke', 'say joke')
        for item in say_joke_keywords:
            if input.startswith(item):
                return True
        return False

    def input_extractor(self, input):
        input = input.lower()

        # Lang should be lang code like: 'en'
        # lang is for Emma to change her voice to lang
        # language is for tell_joke function
        result = { 'category': '', 'language': ''}

        # I except the last word be a language
        supported_langs = tts_langs()
        supported_categories = ('misc', 'programming',
                                'dark', 'pun', 'spooky', 'christmas')
        input_words = input.split()

        lang = ''

        # Find language and category of joke from input
        for i in range(len(input_words)):
            # Language
            if input_words[i] == 'language':
                lang = input_words[i-1]
            # Category
            if input_words[i] == 'category':
                category = input_words[i-1]
                if category in supported_categories:
                    result['category'] = category

        # validate selected language
        if lang in supported_langs.keys():
            result['language'] = result['lang']
        elif lang.capitalize() in supported_langs.values():
            result['language'] = result['lang']

        self.language = result['language']
        self.category = result['category']
        self._set_input_extracted_true()


@__needs_input
@__needs_internet_connection
class SayQuote(IOperation):
    def action(self):
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
        super().action()

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
        if self.all_quotes:
            quotes, number_quotes = get_quotes(url=base_url+'quotes')
            result = quotes + f"\n\nNumber of Quotes: {number_quotes}"

        if self.all_authors:
            result, number_authors = get_all_authors()
            result = result + f"\n\nNumber of Authors: {number_authors}"

        if self.all_authors == True or self.all_quotes == True:
            return result
        # endregion

        # If all_quotes or all_authors were False
        full_url = base_url + 'quotes?'
        if self.author != '':
            full_url = full_url + f'author={self.author}&'
        if self.genre != '':
            full_url = full_url + f'genre={self.genre}'
        full_url += f'&limit={self.limit}'
        result, number_quotes = get_quotes(full_url)

        # Add number of quotes in result
        result = result + f"\n\nNumber of Quotes: {number_quotes}"
        return result

    def checker(input):
        say_quote_keywords = ('say quote', 'give me a quote',
                              'give me a quote', 'say a quote')
        for item in say_quote_keywords:
            if input.startswith(item):
                return True
        return False

    def input_extractor(self, input):
        # If user wants all authors of quotes
        all_authors_keywords = ('all quotes authors',
                                'give me all quotes authors')
        for item in all_authors_keywords:
            if item == input:
                return {'all_authors': True}
        # If user wants all quotes
        all_quotes_keywords = (
            'all qoutes', 'give me all quotes', 'give me all quotes you have')
        for item in all_quotes_keywords:
            if item == input:
                return {'all_quotes': True}

        # If user wants to get quote(quotes) from a genre or an author
        result = {'author': '', 'genre': ''}

        # Input words
        input_words = input.split()

        # Find author name in input
        for i in range(len(input_words)):
            if input_words[i].lower() == 'from':
                result['author'] = str(input_words[i+1])

        # Find genre name in input
        for i in range(len(input_words)):
            if input_words[i].lower() == 'genre':
                result['genre'] = str(input_words[i - 1])

        self.author = result['author']
        self.genre = result['genre']
        self._set_input_extracted_true()
        self._set_input_extracted_true()


@__needs_input
class DetectLanguage(IOperation):
    def action(self):
        super().action()
        '''detect language by text'''
        return classify(self.text)[0]

    def checker(input):
        detect_language_keywords = ('detect', 'language')
        if input.startswith(detect_language_keywords[0]) and input.endswith(detect_language_keywords[1]):
            return True
        elif (input.startswith(detect_language_keywords[0] + '' + detect_language_keywords[1])):
            return True
        return False

    def input_extractor(self, input):
        input = input.replace('detect', '', 1)
        input = input.rsplit('language')[0]
        return input.strip()
        self._set_input_extracted_true()


class ShowDate(IOperation):
    def action(self):
        super().action()
        return f'date is {datetime.datetime.now().date()}'

    def checker(input):
        show_date_keywords = ('what date is it',)
        for item in show_date_keywords:
            if input == item:
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


@__needs_input
@__needs_internet_connection
class Ping(IOperation):
    def action(self):
        super().action()
        param = '-n' if platform.system() == 'Windows' else '-c'
        output = getoutput(f'ping {param} 1 {self.server}')
        return output

    def checker(input):
        ping_keywords = ('ping',)
        for item in ping_keywords:
            if input.startswith(item):
                return True
        return False

    def input_extractor(self, input):
        # remove ping from input
        input = input.split('ping')[1]
        self.server = input.strip()
        self._set_input_extracted_true()


class ShowTime(IOperation):
    def action(self):
        super().action()
        return f'time is {datetime.now().time().replace(microsecond=0)}'

    def checker(input):
        showing_time_keyword = ('show time', "what's time", 'what time is it')
        for item in showing_time_keyword:
            if input == item:
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


class ShowDateTime(IOperation):
    def action(self):
        super().action()
        return f"datetime is {datetime.datetime.now()}"

    @staticmethod
    def checker(input):
        show_date_time_keywords = ('what is datetime')
        for item in show_date_time_keywords:
            if item == input:
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


class SayHello(IOperation):
    def action(self):
        '''saying hello and good(Morning/Afternoon/Evening)'''
        super().action()
        hour = datetime.now().hour
        if hour >= 0 and hour < 12:
            return "Hello, Good Morning"
        elif hour >= 12 and hour < 18:
            return "Hello, Good Afternoon"
        else:
            return "Hello, Good Evening"

    def checker(input):
        say_hello_keyword = ('say hello', 'hello')
        for item in say_hello_keyword:
            if input.startswith(item):
                return True
        return False

    def input_extractor(self):
        self._set_input_extracted_true()


@__needs_input
@__needs_internet_connection
class SearchInWikipedia(IOperation):
    def action(self):
        '''search in wikipedia'''
        super().action()
        result = None
        if self.summary:
            result = wikipedia.summary(self.text)
        else:
            result = wikipedia.page(self.text).content
        return result

    def checker(input):
        search_in_wikipedia_keywords = ('search wikipedia', 'search wiki',
                                        'in wiki', 'in wikipedia', 'search in wiki', 'search in wikipedia')
        for item in search_in_wikipedia_keywords:
            if input.startswith(item) or input.endswith(item):
                return True
        return False

    def input_extractor(self, input):
        inputs: dict[str, bool] = {'text': '', 'summary': True}
        additionals = ('search wikipedia', 'search wiki', 'in wiki',
                       'in wikipedia', 'search in wiki', 'search in wikipedia')
        full_content = ('full content', 'full page')

        for addition in additionals:
            if input.startswith(addition):
                input = input.replace(addition, '')
            if input.endswith(addition):
                input = input.rsplit(addition)[0]

        for item in full_content:
            if item in input:
                inputs['summary'] = False
                input = input.replace(item, '')
                break
        self.text = input.strip()
        self.summary = inputs['summary']
        self._set_input_extracted_true()


@__needs_input
@__needs_internet_connection
class SearchInWeb(IOperation):
    def action(self):
        super().action()
        '''search in the web by default browser'''
        webbrowser.open_new_tab(f'https://duckduckgo.com/?q={self.query}')
        return 'opening browser and searching for result'

    def checker(input):
        search_in_web_keywords = ('search', 'browse')
        for item in search_in_web_keywords:
            if input.startswith(item):
                if not input.startswith('wikipedia') and not input.startswith('wiki'):
                    return True
        return False

    def input_extractor(self, input):
        additionals_start = ('browse', 'search', 'google')
        additionals_end = ('in web', 'in google')
        for additional in additionals_start:
            if input.startswith(additional):
                input = input.replace(additional, '')

        for additional in additionals_end:
            if input.endswith(additional):
                input = input.replace(additional, '')

        self.query = input.strip()
        self._set_input_extracted_true()

# Config global variables


class InternetStatus(IOperation):
    def action(self):
        '''show internet connection status'''
        super().action()
        if GET_GLOBAL_VARS().get('__internet_connection') == True:
            return "You're connect to the internet"
        else:
            return "No internet connection"

    def checker(input):
        internet_status_checker = (
            'check internet connection', 'check internet status', 'check internet')
        for item in internet_status_checker:
            if input == item:
                return True
        return False

    def input_extractor(self, input):
        self._set_input_extracted_true()


class TranslateGoogle(IOperation):
    def action(self):
        '''translate a text with google translation service/api (online)'''
        super().action()
        t = Translator()
        return t.translate(self.text, self.lang).text
    @staticmethod
    def checker(input):
        translate_google_keywords = ('translate',)
        for item in translate_google_keywords:
            if input.startswith(item):
                return True
        return False

    def input_extractor(self, input):
        inputs = {'text': '', 'lang':''}
        # lang in this dictionary is Emma speak language
        try:
            from googletrans import LANGCODES
        except:
            raise Exception(
                'This operation needs to "googletrans" module\nPlease install this module with "pip install googletrans==4.0.0-rc1".\nYou can install latest version but this version works fine so far')

        input = input.replace('translate', '')
        for lang_code in LANGCODES.keys():
            if (input.endswith(f'to {lang_code}')):
                inputs['lang'] = LANGCODES.get(lang_code)
                input = input.replace(f'to {lang_code}', '')

            elif (input.endswith(f'in {lang_code}')):
                inputs['lang'] = LANGCODES.get(lang_code)
                input = input.replace(f'in {lang_code}', '')
        self.text = input.strip()
        self.lang = inputs['lang']
        self._set_input_extracted_true()

@__needs_input
class Cmd(IOperation):
    def action(self):
        '''runs a command in shell and returns the output'''
        super().action()
        if self.command:
            _, output = getstatusoutput(self.command)
            return output
        else:
            return "The command input is empty."


    def checker(input):
        pass

    def input_extractor(self, input):
        self.command = input
        self._set_input_extracted_true()



if not INITIATED :
    GET_GLOBAL_VARS().set('__all_operations',__all_operations())
    INITIATED = True