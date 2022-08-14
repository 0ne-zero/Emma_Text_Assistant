#!/usr/bin/env python3

from core import Core
from state import AudioState, HalfAudioState, StopState, TextState


class Emma():

    __instance_count: int = 0

    def __init__(self, default_state=TextState(), aiml_brain_file="./aiml/brain.brn",
                 aiml_learn_files=['./aiml/learn.aiml', ], aiml_commands=['LOAD AIML', ],
                 save_audio=True, audio_directory="./audios/", save_log=True, log_directory='/var/log/emma/',
                 log_level='DEBUG', use_thread=True, versobe=False) -> None:
        self.core = Core(
            default_state=default_state,aiml_brain_file=aiml_brain_file,aiml_learn_files=aiml_learn_files,
            aiml_commands=aiml_commands,save_audio=save_audio,audio_directory=audio_directory,save_log=save_log,log_directory=log_directory,
            log_level=log_level,use_thread=use_thread,versobe=versobe)

    def set_input(self, input):
        self.core.input['text'] = input

    def processing(self):
        '''Input processing and performing the input request and display the final output'''

        self.core.processing()


emma = Emma()
while(1):
    emma.processing()
