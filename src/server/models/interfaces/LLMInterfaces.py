from abc import ABC,abstractmethod
from typing import List, Dict, Any,Optional, Tuple
from ..enums import LLMExecutionMode,LLMProvider
from langchain.messages import SystemMessage
# ============================================================
# 1. BASE LLM CONFIGURATION ( Local or Remote)
# ============================================================
class BaseLLMConfigurationInterface(ABC):
    """
    Abstract Base Class LLM Configuration Interface
        for both Local and Remote LLMs
    Methods to implement:
        - setup
        - generate_response
        - validate_connection
        - cleanup
    """
    def __init__(self,params: Dict[str, Any]):
        self.mode = None
        self.api_key = None
        self.model_id = None 
        self.base_url = None
        self.client=None 
        self.SYSTEM_MESSAGE: Optional[SystemMessage] = None
        self.history: List[Dict[str, str]] = []
        self.params = params
        self.max_tokens = self.params.get("max_tokens", 2047)
        self.temperature = self.params.get("temperature", 0)
        self._is_connected = False
    
    @abstractmethod
    def setup(self) -> bool:
        """
        setup Model (local or remote)
        Returns: True if success
        """
        pass
    
    @abstractmethod
    def update_system_message(self,text:str):
        """
        Create system message for LLM
        Args:
            text: system prompt text
        Update: SystemMessage object
        """
        pass
    
    @abstractmethod
    def release_history(self):
        """
        Clear conversation history
        """
        pass
    
    @abstractmethod
    def generate_response(self,user_input: str) -> str:
        """
        Core generation method
        Args:
            system_prompt:persona instructions
            history: conversation history
            user_input: current user message
        Returns: Generated text
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Release resources
        """
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.parms
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration dynamically"""
        self.parms.update(new_config)
    
    
    



