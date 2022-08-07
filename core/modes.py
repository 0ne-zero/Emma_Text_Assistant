from enum import Enum
from enum import auto
class Modes(Enum):
    stopped = auto()
    ready = auto()
    command = auto()
    listening=auto()
    processing = auto()
    speaking = auto()