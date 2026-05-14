import pyaudio
import numpy as np
from server.infrastructure.tts import NeuTTS
import threading
import time
from queue import Queue
from server.helpers import get_config
from server.models.enums import TTSCodec,TTSBackbone
from server.models.interfaces import TTSInterface
import os

# Add this BEFORE initializing NeuTTS
os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = r'C:\Program Files\eSpeak NG\libespeak-ng.dll'
os.environ['PHONEMIZER_ESPEAK_PATH'] = r'C:\Program Files\eSpeak NG'
class TTSController(TTSInterface):
    """
    Ultra-smooth TTS Controller for Interview AI Tool
    
    Features:
    - Zero-delay streaming
    - ZERO stuttering - perfectly smooth speech
    - No gaps or lag between words
    - Pre-buffering for seamless playback
    
    Usage:
    -------
    tts = TTSController()
    tts.setup_voice(audio_path, transcript)
    tts.speak(text)  # smooth, natural speech
    """
    
    def __init__(self):
        
        self.config = get_config()
        self.tts_backbone=None
        self.tts_codec=None
        
        if self.config.TTS_BACKBONE=="NANO":
            self.tts_backbone=TTSBackbone.NANO.value
        elif self.config.TTS_BACKBONE=="NANO_Q4":
            self.tts_backbone=TTSBackbone.NANO_Q4.value
        elif self.config.TTS_BACKBONE=="NANO_Q8":
            self.tts_backbone=TTSBackbone.NANO_Q8.value
        elif self.config.TTS_BACKBONE=="AIR_Q4":
            self.tts_backbone=TTSBackbone.AIR_Q4.value
        elif self.config.TTS_BACKBONE=="AIR_Q8":
            self.tts_backbone=TTSBackbone.AIR_Q8.value
        else:
            self.tts_backbone=TTSBackbone.NANO_Q8.value
        
        if self.config.TTS_CODEC=="NEU_CODEC":
            self.tts_codec=TTSCodec.NEU_CODEC.value
        elif self.config.TTS_CODEC=="DISTILL_NEU_CODEC":
            self.tts_codec=TTSCodec.DISTILL_NEU_CODEC.value
        else:
            self.tts_codec=TTSCodec.DISTILL_NEU_CODEC.value

        # TTS Model
        self.tts = NeuTTS(
            backbone_repo=self.tts_backbone,
            backbone_device=self.config.TTS_DEVICE,
            codec_repo=self.tts_codec,
            codec_device=self.config.TTS_CODEC_DEVICE
        )
        
        # CRITICAL: Balance between speed and smoothness
        # Larger chunks = smoother playback but slightly more delay
        self.tts.streaming_overlap_frames=self.config.TTS_STREAMING_OVERLAP_FRAMES
        self.tts.streaming_frames_per_chunk =self.config.TTS_STREAMING_FRAMES_PER_CHUNK # Increased for smoother audio
        self.tts.streaming_lookforward = self.config.TTS_STREAMING_LOOKFORWARD        # Increased for better continuity
        self.tts.streaming_lookback = self.config.TTS_STREAMING_LOOKBACK   # Increased for smoother transitions
        
        self.tts.streaming_stride_samples = self.tts.streaming_frames_per_chunk * self.tts.hop_length
        
        
        # Voice reference
        self.ref_codes = None
        self.ref_text = None
        self._is_connected = False
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Audio buffer for smooth playback
        self.audio_buffer = Queue(maxsize=250)
        self.min_buffer_size = 2
        
        # Control flags
        self.is_speaking = False
        self.is_generating = False
        self.stop_flag = False
        
    
    
    def setup(self, ref_audio_path: str, ref_text_content: str):
        """
        One-time voice encoding
        
        Parameters:
        -----------
        ref_audio_path : str
            Path to voice sample (wav, 3-15 sec recommended)
        ref_text_content : str
            Reference transcript matching the audio
        """
        self.ref_codes = self.tts.encode_reference(ref_audio_path)
        self.ref_text = ref_text_content
        self._is_connected = True
        return self._is_connected   
    
    def speak(self, text: str, wait=True):
        """
        Smooth, natural speech with zero stuttering
        
        Parameters:
        -----------
        text : str
            Text from LLM
        wait : bool
            False = non-blocking (default)
            True = blocking until speech completes
        """

        if not self._is_connected:
            raise RuntimeError("❌ Call setup() first!")
        
        if not text or not text.strip():
            return
        
        # Stop any previous speech
        self.stop()
        
        # Wait for previous to finish
        while self.is_speaking or self.is_generating:
            time.sleep(0.0001)
        
        # Clear buffer
        while not self.audio_buffer.empty():
            try:
                self.audio_buffer.get_nowait()
            except:
                break
        
        # Reset flags
        self.stop_flag = False
        
        # Start generation + playback
        gen_thread = threading.Thread(
            target=self._generate_audio,
            args=(text,),
            daemon=True
        )
        gen_thread.start()
        
        if wait:
            # Wait for generation to finish
            while self.is_generating:
                time.sleep(0.0001)
            # Wait for playback to finish
            while self.is_speaking:
                time.sleep(0.0005)
    
    def _generate_audio(self, text: str):
        self.is_generating = True
        try:
            # ✅ FIX: pad short text to avoid zero-size audio buffer
            MIN_CHARS = 20
            if len(text.strip()) < MIN_CHARS:
                text = text.strip() + "." * (MIN_CHARS - len(text.strip()))

            chunk_count = 0
            for chunk in self.tts.infer_stream(
                text,
                self.ref_codes,
                self.ref_text
            ):
                if self.stop_flag:
                    break

                # ✅ FIX: skip empty chunks to avoid zero-size reduction error
                if chunk is None or chunk.size == 0:
                    continue

                audio_data = chunk.astype(np.float32)

                try:
                    self.audio_buffer.put(audio_data, block=True, timeout=1.0)
                except:
                    if self.stop_flag:
                        break
                    continue

                chunk_count += 1

                if chunk_count == self.min_buffer_size and not self.is_speaking:
                    playback_thread = threading.Thread(
                        target=self._play_audio,
                        daemon=True
                    )
                    playback_thread.start()

            if not self.is_speaking and chunk_count > 0:
                playback_thread = threading.Thread(
                    target=self._play_audio,
                    daemon=True
                )
                playback_thread.start()

        except ValueError as e:
            # ✅ FIX: catch the zero-size numpy error specifically
            if "zero-size array" in str(e):
                import logging
                logging.getLogger(__name__).warning(
                    "TTS skipped: text too short for streaming params. "
                    "Try increasing TTS_STREAMING_FRAMES_PER_CHUNK in config."
                )
            else:
                raise
        except Exception as e:
            print(f"❌ Generation error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_generating = False
    
    def _play_audio(self):
        """
        Play buffered audio smoothly
        Runs in separate thread
        """
        
        self.is_speaking = True
        
        # Open stream with larger buffer for smooth playback
        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=24000,
            output=True,
            frames_per_buffer=self.config.TTS_FRAMES_PER_BUFFER,
            stream_callback=None
        )
        
        try:
            
            # Play all buffered chunks
            while True:
                if self.stop_flag:
                    break
                
                # Get chunk from buffer
                try:
                    chunk = self.audio_buffer.get(block=True, timeout=0.1)
                except:
                    # Buffer empty - check if generation finished
                    if not self.is_generating:
                        # Wait a bit for any remaining chunks
                        time.sleep(0.01)
                        if self.audio_buffer.empty():
                            break
                        else:
                            continue
                    else:
                        # Still generating, wait for more chunks
                        continue
                
                # Write chunk to stream (blocking until space available)
                # This ensures smooth, continuous playback
                try:
                    self.stream.write(chunk.tobytes(), exception_on_underflow=False)
                except:
                    if self.stop_flag:
                        break
                    continue

            
        except Exception as e:
            print(f"❌ Playback error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Close stream
            if self.stream:
                try:
                    # Drain remaining audio to prevent cutoff
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
                self.stream = None
            
            self.is_speaking = False
    
    def stop(self):
        """
        Immediately stop current speech
        """
        self.stop_flag = True
        
        # Clear buffer
        while not self.audio_buffer.empty():
            try:
                self.audio_buffer.get_nowait()
            except:
                break
        
        # Wait for threads to stop
        timeout = time.time() + 1.0
        while (self.is_speaking or self.is_generating) and time.time() < timeout:
            time.sleep(0.001)
    
    def wait_until_done(self):
        """
        Wait until current speech completes
        """
        while self.is_speaking or self.is_generating:
            time.sleep(0.0001)
    
    def cleanup(self):
        self.stop()

        # ✅ FIX: force llama __del__ to run NOW while ctypes lib is still alive
        if hasattr(self, 'tts') and self.tts is not None:
            try:
                if hasattr(self.tts, 'backbone') and self.tts.backbone is not None:
                    if hasattr(self.tts.backbone, 'close'):
                        self.tts.backbone.close()
                    self.tts.backbone = None
            except Exception:
                pass
            del self.tts          # trigger __del__ explicitly
            self.tts = None

            import gc
            gc.collect()          # ✅ force destructor to run immediately

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None

