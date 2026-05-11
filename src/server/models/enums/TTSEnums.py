from enum import Enum

class TTSBackbone(Enum):
    NANO = "neuphonic/neutts-nano"
    NANO_Q4 = "neuphonic/neutts-nano-q4-gguf"
    NANO_Q8 = "neuphonic/neutts-nano-q8-gguf"
    AIR_Q4 = "neuphonic/neutts-air-q4-gguf"
    AIR_Q8 = "neuphonic/neutts-air-q8-gguf"
    
class TTSCodec(Enum):
    NEU_CODEC = "neuphonic/neucodec"
    DISTILL_NEU_CODEC = "neuphonic/distill-neucodec"