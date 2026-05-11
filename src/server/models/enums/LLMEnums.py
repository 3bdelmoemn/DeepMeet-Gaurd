from enum import Enum

class LLMExecutionMode(Enum):
    LOCAL = "local"
    REMOTE = "remote"

class LLMProvider(Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    COHERE="cohere"