#!/usr/bin/env python3

from core import Core
from globals import GET_GLOBAL_VARS
from state import TextState
class Emma():

    __instance_count: int = 0
    def __init__(self,default_state=TextState(), brain_file="brain.brn",
                 learn_files=['learn.aiml', ], commands=['LOAD AIML', ],
                 chdir='aiml', save_log=True, log_file_location='/var/log/emma/',
                 log_level='DEBUG', use_thread=False, versobe=False) -> None:
        self.core = Core(default_state,brain_file,learn_files,commands,chdir,save_log,log_file_location,log_level,use_thread,versobe)

    def processing(self):
        '''Input processing and performing the input request and display the final output'''

        self.core.processing()


emma = Emma()
while(1):
    emma.processing()
