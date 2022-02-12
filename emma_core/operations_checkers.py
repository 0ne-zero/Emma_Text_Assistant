class Checkers:

    @staticmethod
    def all_public_checkers():
        return [checker for checker in dir(Checkers) if not checker.startswith("_") and checker.endswith("checker")]

    @staticmethod
    def show_datetime_checker(input: str):
        showing_time_keyword = ('show time', "what's time", 'what time is it')
        for item in showing_time_keyword:
            if input == item:
                return True
        return False

    def ping_counter_checker(input: str):
        ping_counter_keyword = ('tell me ping counter', 'how many times pinged',
                                'ping counter', 'tell me how many times you pinged')
        for item in ping_counter_keyword:
            if input == item:
                return True
        return False

    @staticmethod
    def say_hello_checker(input: str):
        say_hello_keyword = ('say hello', 'hello')
        for item in say_hello_keyword:
            if input.startswith(item):
                return True
        return False

    @staticmethod
    def run_checker(input: str):
        run_keywords = ('start', 'start yourself', 'please start yourself',
                        'run', 'run yourself', 'please run yourself')
        for item in run_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def instance_count_checker(input: str):
        instance_count_keywords = (
            'instance count', 'how many instance of you exist in this program', 'how many instance of you exist')
        for item in instance_count_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def user_operations_checker(input: str):
        user_operations_keywords = (
            'all operation', 'what\'s your all ability', 'what can you do', 'all ability')
        for item in user_operations_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def stop_checker(input: str):
        stop_keywords = ('stop', 'stop yourself', 'please stop yourself')
        for item in stop_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def search_in_wikipedia_checker(input: str):
        search_in_wikipedia_keywords = ('search wikipedia', 'search wiki',
                                        'in wiki', 'in wikipedia', 'search in wiki', 'search in wikipedia')
        for item in search_in_wikipedia_keywords:
            if input.startswith(item) or input.endswith(item):
                return True
        return False

    @staticmethod
    def open_website_checker(input: str):
        open_website_keywords = ('open', 'browse', 'google')
        for item in open_website_keywords:
            if input.startswith(item) and input.endswith('website'):
                return True
        return False

    @staticmethod
    def translate_google_checker(input: str):
        translate_google_keywords = ('translate',)
        for item in translate_google_keywords:
            if input.startswith(item):
                return True
        return False

    @staticmethod
    def shutdown_system_checker(input: str):
        shutdown_system_keywords = (
            'shutdown', 'shutdown system', 'halt system')
        for item in shutdown_system_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def cancel_shutdowning_system_checker(input: str):
        cancle_shutdowning_keywords = (
            'cancel shutdown', 'cancle shutdowning', 'cancel shutdown system')
        for item in cancle_shutdowning_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def reboot_system_checker(input: str):
        reboot_system_keywords = ('reboot', 'reboot system')
        for item in reboot_system_keywords:
            if input == item:
                return True
        return False

    @staticmethod
    def search_in_web_checker(input: str):
        search_in_web_keywords = ('search', 'browse')
        for item in search_in_web_keywords:
            if input.startswith(item):
                if not input.startswith('wikipedia') and not input.startswith('wiki'):
                    return True
        return False

    @staticmethod
    def create_directory_checker(input:str):
        create_directory_keywords = ("create directory","create folder")
        for item in create_directory_keywords:
            if input.startswith(item):
                return True
        return False

    def command_mode_checker(input:str):
        command_mode_checker = ('command mode','go to command mode','goto command mode')
        for item in command_mode_checker:
            if input == item:
                return True
        return False
    @staticmethod
    def detect_language_checker(input: str):
        detect_language_keywords = ('detect', 'language')
        if input.startswith(detect_language_keywords[0]) and input.endswith(detect_language_keywords[1]):
            return True
        elif (input.startswith(detect_language_keywords[0] + '' + detect_language_keywords[1])):
            return True
        return False

    @staticmethod
    def change_speaking_language_checker( input: str):
        change_speaking_language = (
            'change language', 'change your language to')
        for item in change_speaking_language:
            if input.startswith(item):
                return True
        return False
