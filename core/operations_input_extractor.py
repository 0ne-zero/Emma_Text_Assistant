from platform import system as system_name
from subprocess import getoutput
from gtts.tts import tts_langs

from core import utilities
class OperationInputExtractor():

    @staticmethod
    def search_in_web_input_manipulator(input: str):
        # input manipulation
        additionals_start = ('browse', 'search', 'google')
        additionals_end = ('in web', 'in google')
        for additional in additionals_start:
            if input.startswith(additional):
                input = input.replace(additional, '')

        for additional in additionals_end:
            if input.endswith(additional):
                input = input.replace(additional, '')

        return input.strip()

    @staticmethod
    def detect_language_input_manipulator(input: str):
        input = input.replace('detect', '', 1)
        input = input.rsplit('language')[0]
        return input.strip()

    @staticmethod
    def search_in_wikipedia_input_manipulator(input: str):
        inputs: dict[str, bool, bool] = {'text': '', 'summary': True}
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

        inputs['text'] = input.strip()

        return inputs

    @staticmethod
    def translate_google_input_manipulator(input: str):

        inputs = {'text': '', 'dest_lang': '', 'lang': ''}
        # lang in this dictionary is Emma speak language
        try:
            from googletrans import LANGCODES
        except:
            raise Exception(
                'This operation needs to "googletrans" module\nPlease install this module with "pip install googletrans==4.0.0-rc1".\nYou can install latest version but this version works fine so far')

        input = input.replace('translate', '')
        for lang_code in LANGCODES.keys():
            if (input.endswith(f'to {lang_code}')):
                inputs['dest_lang'] = LANGCODES.get(lang_code)
                input = input.replace(f'to {lang_code}', '')

            elif (input.endswith(f'in {lang_code}')):
                inputs['dest_lang'] = LANGCODES.get(lang_code)
                input = input.replace(f'in {lang_code}', '')

        inputs['text'] = input.strip()
        inputs['lang'] = inputs['dest_lang']
        return inputs

    @staticmethod
    def create_directory_input_manipulator(input: str):
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
                if system_name() == "Linux":
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
                elif system_name() == "Windows":
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

        return inputs

    @staticmethod
    def open_website_input_manipulator(input: str):
        additionals_start = ('browse', 'search', 'google')
        input = input.replace('website', '')
        for additional in additionals_start:
            if input.startswith(additional):
                input = input.replace(additional, '')

        return input.strip()

    @staticmethod
    def show_datetime_input_manipulator(input: str):
        pass

    @staticmethod
    def aiml_response_input_manipulator(input: str):
        return input.strip()

    @staticmethod
    def say_quote_input_manipulator(input: str):
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

        return result

    def tell_joke_input_manipulator(input:str):
        
        input = input.lower()
        
        # Lang should be lang code like: 'en'
        # lang is for Emma to change her voice to lang
        # language is for tell_joke function
        result = {'lang':'','category':'','language':''}

        # I except the last word be a language 
        supported_langs = tts_langs()
        supported_categories = ('misc','programming','dark','pun','spooky','christmas')
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
            result['lang'] = lang
            result['language'] = result['lang']
        elif lang.capitalize() in supported_langs.values():
            result['lang'] = utilities.get_key_by_value(lang,supported_langs)
            result['language'] = result['lang']

        return result



    def change_speaking_language_input_manipulator(input: str):
        additionals_start = ('change language to', 'change your language to')
        for item in additionals_start:
            if input.startswith(additionals_start):
                input = input.replace(item, '')

        return input.strip()

    @staticmethod
    def get_input_manipulator_by_operation_name(operation_name):
        '''Return operation input manipulator function by operation name'''
        input_manipulator_func = eval(
            f'OperationInputManipulation.{operation_name}_input_manipulator')
        return input_manipulator_func
