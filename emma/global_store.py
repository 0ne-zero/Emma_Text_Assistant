class GlobalStore():
    '''
    This class has private variable that are can be accessed across program
    Core class has a instace of this class
    '''

    '''
        In python i can't do something like this:
        string = "blah blah blah   \"
        If backslash be in end of string at least vs code throw "String literal is unterminated"
        My solution is written in below line and in finally maybe just i don't know how do this...
    '''
    __backslash = '\ '.strip()
    def set(self, k, v):
        if k.strip() == "" or v == None:
            raise Exception("the k or v is empty")

        # make attr private
        k = self.__make_var_name_private(k)

        setattr(self, k, v)

    def get(self, k):
        '''If k doesn't exists returns None'''
        if k.strip() == '':
            raise Exception("the k is empty")

        # make attr private
        k = self.__make_var_name_private(k)

        return getattr(self, k, None)

    def __make_var_name_private(self,var_name) -> str:
        if not var_name.startswith('_Global_Vars'):
            return f'_{self.__class__.__name__}{var_name}'
        return var_name