from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8")
    #======================== APP Info =========================#
    APP_NAME:str
    APP_VERSION:str
    # ======================= storage Configuration ================#
    SIMULATOR_STORAGE_PATH:str=None
    DETECTOR_STORAGE_PATH:str=None

    #======================== LLM Configuration ================#
    # Mode:
    LLM_MODE:str=None

    OPEN_AI_BASE_URL:str=None
    OLLAMA_BASE_URL:str=None
    GROQ_BASE_URL:str=None
    
    # Provider:
    LLM_PROVIDER:str=None
 

    # API Keys:
    OPENAI_API_KEY:str=None
    CLAUDE_API_KEY:str=None
    GEMINI_API_KEY:str=None
    COHERE_API_KEY:str=None
    OLLAMA_API_KEY:str=None
    
    #  Model IDs:

    OPENAI_MODEL_ID:str=None
    CLAUDE_MODEL_ID:str=None
    GEMINI_MODEL_ID:str=None
    COHERE_MODEL_ID:str=None
    OLLAMA_MODEL_ID:str=None
    
    # parameters:
    MAX_TOKENS:int=None
    CONTEXT_WINDOW:int=None
    MAX_INPUT_TOKENS:int=None
    TEMPERATURE:float=None
    # history_messages:
    HISTORY_MESSAGES:int=None
    #======================== TTS Configuration ================#
    # TTS Model Configuration
    TTS_BACKBONE:str=None
    TTS_CODEC:str=None
    TTS_DEVICE:str=None
    TTS_CODEC_DEVICE:str=None
    # TTS STREAMING SETTINGS (CRITICAL - DO NOT CHANGE)
    TTS_STREAMING_OVERLAP_FRAMES:int=0
    TTS_STREAMING_FRAMES_PER_CHUNK:int=80
    TTS_STREAMING_LOOKFORWARD:int=0
    TTS_STREAMING_LOOKBACK:int=0

    #TTS PLAYBACK SETTINGS (OPTIMIZED)
    TTS_SAMPLE_RATE:int=24000
    TTS_FRAMES_PER_BUFFER:int=1024
    TTS_MIN_BUFFER_SIZE:int=10
    TTS_AUDIO_QUEUE_SIZE:int=1000
    DEFAULT_REF_AUDIO_PATH:str=None
    DEFAULT_REF_TEXT_PATH:str=None
    COOLDOWN_SECONDS:float=None
# ========================= STT Configuration ================#
    STT_MODEL_PATH:str=None
    MIN_WORDS:int=None
    DEDUP_TTL:float=None
# ========================= Detection Configuration ================#
    LAYER_ONE_NAME:str="Spectra0"
    LAYER_ONE_WEIGHT:float=1

    LAYER_TWO_NAME:str="VIT"
    LAYER_TWO_WEIGHT:float=1
    VIT_DATASET_NAME:str="ASVspoof5"
    VIT_VISIUALIZATION:str="MelSpectrogram"
    LAYER_THREE_NAME:str="RawNet2"
    LAYER_THREE_WEIGHT:float=1

    LAYER_FOUR_NAME:str="liveness"
    LAYER_FOUR__MODELPATH:str=r"src\server\infrastructure\behaviour_liveness_detection_model"
    LAYER_FOUR_WEIGHT:float=1

def get_config()->Config:
    return Config()