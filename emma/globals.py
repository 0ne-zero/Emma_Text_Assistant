


__GLOBAL_VARS = None
__INITIATED = False


def GET_GLOBAL_VARS():
    global __GLOBAL_VARS
    if __GLOBAL_VARS == None:
        __GLOBAL_VARS = __Global_Vars
        return __GLOBAL_VARS
    else:
        return __GLOBAL_VARS

class __Global_Vars():

    @classmethod
    def set(cls,k, v):
        if k.strip() == "" or v == None:
            raise Exception("the k or v is empty")

        # make attr private
        if not k.startswith("__"):
            k = cls.__make_var_name_private(k)

        
        setattr(globals()['__GLOBAL_VARS'], k, v)

    @classmethod
    def get(cls,k):
        '''If k doesn't exists returns None'''
        if k.strip() == '':
            raise Exception("the k is empty")
        
        # make attr private
        if not k.startswith("__"):
            k = cls.__make_var_name_private(k)

        return getattr(globals()['__GLOBAL_VARS'], k,None)

    def __make_var_name_private(var_name)->str:
        if not var_name.startswith('__'):
            return f'__{var_name}'
        return var_name



if not __INITIATED:
    __GLOBAL_VARS = __Global_Vars
    __INITIATED = True