from typing import Any


class GlobalStore():
    '''
    It's just a dictionary with get and set methods
    Core class has a instace of this class
    '''

    '''
        In python i can't do something like this:
        string = "blah blah blah   \"
        If backslash be in end of string at least vs code throw "String literal is unterminated"
        My solution is written in below line and in finally maybe just i don't know how do this...
    '''

    def __init__(self) -> None:
        self.store = {}
        self.store['backslash'] = '\\'.strip()

    def set(self, k: str, v: Any):
        if k.strip() == "" or v == None:
            raise Exception("the k or v is empty")

        self.store[k] = v

    def get(self, k: str):
        '''If k doesn't exists returns None'''
        if k.strip() == '':
            raise Exception("the k is empty")

        return self.store.get(k, None)
