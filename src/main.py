from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from detection_spectral0 import analyze_with_spectral0
from models.Behaviour_Liveness import VoiceDeepfakeDetector
import os
import threading
import time
import pyaudio
import wave
import tempfile
import librosa
import numpy as np
from datetime import datetime
import logging
import soundfile as sf
import soundcard as sc
import tensorflow as tf
from utilities import (
    convert_audio_to_image,
    load_and_crop_tf,
    preprocess_efficientnet
)

# ============================================================
# Import routers (no set_globals needed anymore)
# ============================================================
from routers import (
    health_router,
    setup_router,
    chat_router,
    detection_router,
    cleanup_router
)

# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(title="DeepMeet Guard API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Global Variables
# ============================================================
assistant = None
user_audio_path = None
user_text_path = None
stt_thread = None
stop_listening = False

last_interviewer_text = ""
last_ai_response = ""
state_lock = threading.Lock()

# Detection globals
last_detection_result = {
    "timestamp": None,
    "score": 0,
    "verdict": "unknown",
    "layer1": 0,
    "layer2": 0,
    "layer3": 0,
    "layer4": 0
}
detection_thread = None
detection_stop_flag = False
loopback_device_index = None

# ============================================================
# Helper Functions
# ============================================================
def print_separator(title: str = ""):
    print("\n" + "=" * 60)
    if title:
        print(f"📌 {title}")
    print("=" * 60)



def record_speaker_audio(duration: int = 8, sample_rate: int = 44100):
    print("🎙️ Recording directly from system speakers (WASAPI Loopback)...")
    
    try:
        # 1. بنسأل ويندوز: إيه السماعة الأساسية اللي مطلعة صوت دلوقتي؟
        default_speaker = sc.default_speaker()
        
        # 2. بنجيب المايك الافتراضي اللي بيسجل من السماعة دي (Loopback)
        mics = sc.all_microphones(include_loopback=True)
        loopback_mic = None
        
        for mic in mics:
            if mic.isloopback and mic.name == default_speaker.name:
                loopback_mic = mic
                break
                
        # لو ملقاش الـ Loopback (نادر جداً)، هيستخدم المايك العادي كاحتياطي
        if not loopback_mic:
            print("⚠️ Loopback not found, falling back to default mic.")
            loopback_mic = sc.default_microphone()
            
        # 3. بدء التسجيل!
        with loopback_mic.recorder(samplerate=sample_rate, channels=2) as mic:
            recording = mic.record(numframes=sample_rate * duration)
            
        # 4. حفظ الملف
# 4. حفظ الملف
            os.makedirs("detection_audio", exist_ok=True)
            filename = f"speaker_{int(time.time())}.wav"

            # Create the relative path: "detection_audio/speaker_123.wav"
            relative_filepath = os.path.join("detection_audio", filename)

            # Convert THAT relative path into an absolute path
            filepath = os.path.abspath(relative_filepath)

            sf.write(filepath, recording, sample_rate)
            print(f"✅ Saved successfully: {filepath}")
            return filepath
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return None
# def analyze_speaker_audio(audio_path: str, delete_after: bool = True) -> dict:
#     try:
#         audio, sr = librosa.load(audio_path, sr=16000)
#         energy = np.mean(np.abs(audio))
#         zero_crossings = np.mean(librosa.feature.zero_crossing_rate(audio))
#         score = int(50 + (zero_crossings * 20))
#         score = min(100, max(0, score))
#         verdict = "deepfake" if score > 70 else "suspicious" if score > 40 else "authentic"
        
#         result = {
#             "score": score,
#             "verdict": verdict,
#             "duration": round(len(audio) / sr, 2),
#             "energy": round(energy, 4),
#             "file_path": audio_path  # إضافة مسار الملف للنتيجة
#         }
    
#         # if delete_after and os.path.exists(audio_path):
#         #     os.remove(audio_path)
#         #     print(f"🗑️ Deleted temp file: {audio_path}")
        
#         return result
        
#     except Exception as e:
#         print(f"❌ Analysis error: {e}")
#         return {"score": 0, "verdict": "error"}


def start_periodic_detection():
    global last_detection_result, detection_stop_flag
    print("\n🔍 Starting Speaker Voice Detection...")
    print("   Analyzing every 60 seconds (10-second samples)")

    def detection_loop():
        while not detection_stop_flag:
            try:
                print("\n" + "=" * 50)
                print(f"Detection at {datetime.now().strftime('%H:%M:%S')}")
                audio_path = record_speaker_audio(duration=8)
                if audio_path:
                    image_path=r"C:\Users\Panda\Desktop\DeepMeet\DeepMeet-Guard\server\src\detection_audio\output_images\test.png"
                    convert_audio_to_image(audio_path,image_path)
                    image_test=load_and_crop_tf(image_path)
                    image_test=tf.image.resize(image_test,[224,224])
                    image_test=preprocess_efficientnet(image_test)

                    layer3_result=tf.keras.models.load_model(r"C:\Users\Panda\Desktop\DeepMeet\DeepMeet-Guard\server\src\models\ADFD_CNN_module\artifacts\ADFD_EfficientNet.keras")
                    layer1_result = analyze_with_spectral0(audio_path)
                    print(f"  Layer 1 (Spectral0): {layer1_result['score']}% - {layer1_result['verdict']}")
                    layer2_result = {"score": 50, "verdict": "unknown", "confidence": 0}
                    if behave_live_detector:
                        try:
                            result = behave_live_detector.detect(audio_path)
                            
                            if result['status'] == 'success':
                                ai_prob = result['ai_probability']
                                score = int(ai_prob * 100)
                                
                                if score > 70:
                                    verdict = "deepfake"
                                elif score > 40:
                                    verdict = "suspicious"
                                else:
                                    verdict = "authentic"
                                
                                layer2_result = {
                                    "score": score,
                                    "verdict": verdict,
                                    "confidence": int(result['confidence'] * 100),
                                    "prediction": result['prediction']
                                }
                                print(f"   🧠 Layer 2 (BehaveLive): {score}% - {verdict} (Confidence: {layer2_result['confidence']}%)")
                            else:
                                print(f" BehaveLive error: {result.get('message')}")
                                
                        except Exception as e:
                            print(f" BehaveLive exception: {e}")
                    else:
                        print(" BehaveLive detector not ready yet")
                
                    if layer2_result['score'] != 50: 
                        combined_score = int(layer1_result['score'] * 0.7 + layer2_result['score'] * 0.3)
                        if combined_score > 70:
                            combined_verdict = "deepfake"
                        elif combined_score > 40:
                            combined_verdict = "suspicious"
                        else:
                            combined_verdict = "authentic"
                    else:
                        combined_score = layer1_result['score']
                        combined_verdict = layer1_result['verdict']
                    last_detection_result = {
                        "timestamp": datetime.now().isoformat(),
                        "score": combined_score,
                        "verdict": combined_verdict,
                        "layer1": layer1_result['score'],           # Spectral0
                        "layer2": layer2_result['score'],           # BehaveLive
                        "layer3": layer2_result.get('confidence', 0), # Confidence
                        "layer4": combined_score,
                        "abdelmoemn":np.ravel(layer3_result.predict(tf.expand_dims(image_test,axis=0)))                   # Combined score
                    }
                    
                    print(f"\nCOMBINED RESULT:")
                    print(f"   Layer1 (Spectral0): {layer1_result['score']}%")
                    print(f"   Layer2 (BehaveLive): {layer2_result['score']}%")
                    print(f"   abdelmoemn: {np.ravel(layer3_result.predict(tf.expand_dims(image_test,axis=0)))}")
                    print(f"   FINAL: {combined_score}% - {combined_verdict}")
                    
                    # اختياري: امسحي الملف بعد التحليل
                    # if os.path.exists(audio_path):
                    #     os.remove(audio_path)
                for _ in range(60):
                    if detection_stop_flag:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"Detection error: {e}")
                time.sleep(10)
    thread = threading.Thread(target=detection_loop, daemon=True)
    thread.start()
    return thread

def init_behave_live_detector():
    global behave_live_detector
    print("Initializing BehaveLive Voice Deepfake Detector...")
    model_dir = os.path.join(os.path.dirname(__file__),"models", "Behaviour_Liveness")
    try:
        behave_live_detector = VoiceDeepfakeDetector(model_dir=model_dir)
        print("BehaveLive Detector ready!")
        return True
    except Exception as e:
        print(f"Failed to load BehaveLive Detector: {e}")
        return False

def start_continuous_listening():
    global assistant, stop_listening, last_interviewer_text, last_ai_response
    if assistant is None:
        print("❌ Assistant not initialized")
        return
    print("💡 Speak naturally — I'll wait until you finish\n")
    audio_buffer = []
    silence_counter = 0
    speaking_detected = False
    is_processing = False
    cooldown_until = 0
    MIN_PHRASE_LEN = 3
    MAX_SILENCE_BEFORE_REPLY = 25
    COOLDOWN_AFTER_REPLY = 2.0
    try:
        assistant.stt.start()
        while not stop_listening:
            current_time = time.time()
            if current_time < cooldown_until:
                time.sleep(0.05)
                continue
            elif is_processing:
                is_processing = False
                print("🎙️ Ready for next question...")
            text = assistant.stt.get_new_text()
            if text and len(text.strip()) > 1:
                if not speaking_detected:
                    speaking_detected = True
                    print("\n🎙️ Speaking detected...", end="", flush=True)
                new_word = text.strip()
                if not audio_buffer or new_word != audio_buffer[-1]:
                    audio_buffer.append(new_word)
                silence_counter = 0
                full_text = " ".join(audio_buffer)
                print(f"\r📝 You said: {full_text}", end="", flush=True)
            else:
                if speaking_detected:
                    silence_counter += 1
                    if silence_counter >= MAX_SILENCE_BEFORE_REPLY and len(audio_buffer) > 0 and not is_processing:
                        print()
                        full_phrase = " ".join(audio_buffer)
                        cleaned = full_phrase.strip()
                        if len(cleaned) > MIN_PHRASE_LEN:
                            print(f"\n🔵 [Interviewer]: {cleaned}")
                            last_interviewer_text = cleaned
                            is_processing = True
                            try:
                                response = assistant.llm.generate_response(cleaned)
                                print(f"🔴 [Attacker]: {response}")
                                last_ai_response = response
                                assistant.tts.speak(response)
                                print("🎤 Attacker speaking...\n")
                            except Exception as e:
                                print(f"❌ Generation error: {e}")
                            audio_buffer = []
                            silence_counter = 0
                            speaking_detected = False
                            cooldown_until = time.time() + COOLDOWN_AFTER_REPLY
                            print("🎙️ Listening again after cooldown...")
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ STT error: {e}")
    finally:
        print("🛑 Listening stopped")

def start_detection_on_startup():
    """Start detection after server is fully running"""
    global detection_stop_flag, detection_thread  # ✅ لازم الـ global هنا
    import time
    time.sleep(5)  
    
    if detection_stop_flag is False and detection_thread is None:
        print("🚀 Auto-starting speaker detection...")
        detection_stop_flag = False
        detection_thread = start_periodic_detection()
        print("✅ Speaker detection active (every 60s)")
# ============================================================
# Register routers
# ============================================================
app.include_router(health_router)
app.include_router(setup_router)
app.include_router(chat_router)
app.include_router(detection_router)
app.include_router(cleanup_router)

threading.Thread(target=init_behave_live_detector, daemon=True).start()
# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    import uvicorn

    # Disable access logs
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn").setLevel(logging.WARNING)

    print("\n" + "=" * 60)
    print("🚀 DeepMeet Guard API Server")
    print("=" * 60)
    print("Server: http://localhost:8000")
    print("Docs:   http://localhost:8000/docs")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)