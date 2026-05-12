import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import numpy as np
import threading
import time
import sys
import os
from server.helpers import get_config

# حاولت أحافظ على نفس نمط الـ Imports بتاعتك
# لو عندك ملف config زي الـ TTS، ممكن تستخدمه هنا
# from helpers import get_config 

class STTController:
    """
    Ultra-smooth STT Controller (Vosk Based)
    
    Features:
    - Zero-loss buffering (Queue-based)
    - Background processing (Non-blocking)
    - Auto-reconnect capability
    - System Audio / Microphone support
    
    Usage:
    -------
    stt = STTController()
    stt.setup(model_path)
    stt.start()
    
    while True:
        text = stt.get_new_text()
        if text:
            print(text)
    """
    
    def __init__(self):
        # Configuration placeholders (Match your config style)
        self.config=get_config()
        self.sample_rate = 16000
        self.block_size = 4000  # Optimized for speed (0.25s latency)
        self.channels = 1       # Vosk needs Mono, but we capture Stereo and convert
        
        # State Flags
        self._is_running = False
        self._is_connected = False
        self.stop_flag = False
        
        # Resources
        self.model = None
        self.recognizer = None
        self.stream = None
        
        # Buffers
        # audio_queue: بيخزن الصوت الخام عشان مفيش حاجة تضيع
        self.audio_queue = queue.Queue()
        # text_queue: بيخزن النص الجاهز عشان الـ Controller ياخده
        self.text_queue = queue.Queue()
        
        # Threads
        self.process_thread = None

    def setup(self, model_path: str=None, device_index=None):
        """
        Initialize the Model and Audio Device settings
        """
        if model_path is None or len(model_path.strip()) == 0:
            model_path = self.config.STT_MODEL_PATH
        if self._is_connected:
            print("⚠️ STT is already connected.")
            return

        print(f"⏳ Loading STT Model from: {model_path} ...")
        
        if not os.path.exists(model_path):
            model_path=self.config.STT_MODEL_PATH
            print("model path not exist replacing with default path: ",model_path)

        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.device_index = device_index
            self._is_connected = True
            print("✅ STT Engine Ready.")
            return self._is_connected
        except Exception as e:
            print(f"❌ STT Setup Error: {e}")
            raise e

    def start(self):
        """
        Start capturing and transcribing in background threads
        """
        if not self._is_connected:
            raise RuntimeError("❌ Call setup() first!")
            
        if self._is_running:
            return

        self.stop_flag = False
        self._is_running = True
        
        # Clear queues to avoid processing old audio
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()
        
        print("🎧 STT Stream Started...")

        # 1. Start Audio Stream (Producer)
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                device=self.device_index, 
                dtype='float32',
                channels=2, # Capture Stereo (System Audio usually Stereo)
                callback=self._audio_callback
            )
            self.stream.start()
        except Exception as e:
            print(f"❌ Audio Stream Error: {e}")
            self._is_running = False
            return

        # 2. Start Processing Thread (Consumer)
        self.process_thread = threading.Thread(
            target=self._transcription_worker,
            daemon=True
        )
        self.process_thread.start()

    def stop(self):
        """
        Stop streaming and processing gently
        """
        self.stop_flag = True
        self._is_running = False
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
            
        if self.process_thread:
            self.process_thread.join(timeout=1.0)
            
        print("🛑 STT Stream Stopped.")

    def get_new_text(self):
        """
        Non-blocking retrieval of detected text.
        Returns None if no text is available.
        """
        try:
            return self.text_queue.get_nowait()
        except queue.Empty:
            return None

    def cleanup(self):
        """
        Release all resources
        """
        self.stop()
        self.model = None
        self.recognizer = None
        self._is_connected = False
        print("✅ STT Cleanup complete!")

    # ================= INTERNAL METHODS =================

    def _audio_callback(self, indata, frames, time, status):
        """
        High-priority callback: Just grabs audio and puts it in buffer.
        NO processing here to prevent audio drops.
        """
        if status:
            print(f"⚠️ Audio Status: {status}", file=sys.stderr)
            
        if self.stop_flag:
            return

        # Convert to Mono for Vosk
        mono_data = np.mean(indata, axis=1)
        
        # Convert to Int16 PCM
        pcm_data = (mono_data * 32767).astype(np.int16).tobytes()
        
        self.audio_queue.put(pcm_data)

    def _transcription_worker(self):
        """
        Background worker that processes the audio queue
        """
        while not self.stop_flag:
            try:
                # Wait for audio data (with timeout to check stop_flag)
                data = self.audio_queue.get(timeout=0.5)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.text_queue.put(text) # Push to Main App
                else:
                    # Partial results could be handled here if needed
                    pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Transcribe Error: {e}")


# ==========================================
# ضيف ده في آخر الملف عشان تجرب الكلاس
# ==========================================
# if __name__ == "__main__":
#     # 1. مسار الموديل (تأكد إنه صح)
#     MODEL_PATH = r"D:\Education\Voice & Shield\Audio-Cloning-Detection\server\src\infrastructure\stt\vosk-model-en-us-0.22"

#     stt = STTController()
    
#     try:
#         # 2. التجهيز والتشغيل
#         # لو عايز تحدد المايك/الكابل، ابعت device_index هنا
#         stt.setup(MODEL_PATH) 
#         stt.start()
        
#         print("🚀 System is running... (Press Ctrl+C to stop)")

#         # 3. اللوب دي هي اللي بتخلي البرنامج ميفصلش!
#         while True:
#             # هات الكلام من الطابور (Queue)
#             text = stt.get_new_text()
            
#             if text:
#                 print(f"📝 Detected: {text}")
            
#             # ريح البروسيسور جزء من الثانية
#             time.sleep(0.1)

#     except KeyboardInterrupt:
#         print("\n👋 Stopping...")
#         stt.cleanup()