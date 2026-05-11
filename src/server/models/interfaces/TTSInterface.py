from abc import ABC, abstractmethod


class TTSInterface(ABC):
    """
    Interface for Text-to-Speech Controllers
    
    Defines the contract for any TTS implementation
    (NeutTS, ElevenLabs, Coqui, etc.)
    """

    @abstractmethod
    def setup(self, ref_audio_path: str, ref_text_content: str) -> bool:
        """
        Initialize and encode the reference voice
        
        Args:
            ref_audio_path (str): Path to reference voice audio
            ref_text_content (str): Transcript of the reference audio
        
        Returns:
            bool: True if setup succeeded
        """
        pass

    @abstractmethod
    def speak(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech and play it
        
        Args:
            text (str): Input text to synthesize
            wait (bool): Block until playback finishes
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Immediately stop any ongoing speech
        """
        pass

    @abstractmethod
    def wait_until_done(self) -> None:
        """
        Block until speech generation and playback complete
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Release all audio and model resources
        """
        pass
