

def show_time_checker(input):
    showing_time_keyword = ('show time', "what's time", 'what is time')
    for item in showing_time_keyword:
        if input == item:
            return True
    return False


def say_hello_checker(input):
    say_hello_keyword = ('say hello', 'hello')
    for item in say_hello_keyword:
        if input == item:
            return True
    return False


def wikipedia_search_checker(input):
    wikipedia_search_keyword = ('search wikipedia', 'search wiki')
    for item in wikipedia_search_keyword:
        if input.startwith(item):
            return True
    return False


def open_website_checker(input: str):
    open_website_keyword = ('open', 'browse')
    for item in open_website_keyword:
        if input.startwith(item) and input.endswith('website'):
            return True
    return False


def shutdown_system_checker(input: str):
    shutdown_system_keyword = ('shutdown', 'shutdown system', 'halt system')
    for item in shutdown_system_keyword:
        if input == item:
            return True
    return False


def cancle_shutdowning_system_checker(input: str):
    cancle_shutdowning_keyword = ('cancle shutdown', 'cancle shutdowning')
    for item in cancle_shutdowning_keyword:
        if input == item:
            return True
    return False


def reboot_system_checker(input: str):
    reboot_system_keyword = ('reboot', 'reboot system')
    for item in reboot_system_keyword:
        if input == item:
            return True
    return False


def search_in_web_checker(input: str):
    search_in_web_keyword = ('search', 'browse')
    for item in search_in_web_keyword:
        if input.startswith(item):
            return True
    return False
