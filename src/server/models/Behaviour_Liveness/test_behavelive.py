# F:\DeepMeet\DeepMeet-Guard\server\src\test_behavelive.py

import os
import sys

# أضف المسار الحالي عشان Python يعرف الـ models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.Behaviour_Liveness.Voice_Deepfake import VoiceDeepfakeDetector

def test_single_file(audio_path):
    """
    اختبار BehaveLive Detector على ملف صوتي واحد
    """
    print("=" * 60)
    print("🧪 Testing BehaveLive Deepfake Detector")
    print("=" * 60)
    
    # 1. التحقق من وجود الملف
    if not os.path.exists(audio_path):
        print(f"\n❌ Audio file not found: {audio_path}")
        print("\n💡 Usage:")
        print(f'   python test_behavelive.py "F:/path/to/audio.wav"')
        return
    
    print(f"\n🎵 Testing: {audio_path}")
    print("-" * 40)
    
    # 2. تحميل الـ detector
    print("\n📂 Loading detector...")
    model_dir = os.path.join(os.path.dirname(__file__))
    
    try:
        detector = VoiceDeepfakeDetector(model_dir=model_dir)
    except Exception as e:
        print(f"❌ Failed to load detector: {e}")
        return
    
    # 3. تشغيل التحليل
    print("\n🔍 Analyzing...")
    result = detector.detect(audio_path)
    
    # 4. عرض النتيجة
    if result['status'] == 'success':
        score = int(result['ai_probability'] * 100)
        
        print("\n" + "=" * 40)
        print("📊 RESULTS:")
        print(f"   Prediction     : {result['prediction']}")
        print(f"   AI Probability : {result['ai_probability']:.2%}")
        print(f"   Human Prob     : {result['human_probability']:.2%}")
        print(f"   Confidence     : {result['confidence']:.2%}")
        print(f"   Score (0-100)  : {score}%")
        
    print("\n" + "=" * 60)


if __name__ == "__main__":
    # ============================================================
    # الطريقة الأولى: حددي المسار مباشرة
    # ============================================================
    audio_file = r"C:\Users\Panda\Desktop\DeepMeet\DeepMeet-Guard\server\src\models\spectra_0\Recording.wav"
    test_single_file(audio_file)
    # # ============================================================
    # # الطريقة الثانية: استخدمي أول ملف صوتي موجود في detection_audio
    # # ============================================================
    # if not os.path.exists(audio_file):
    #     detection_folder = r"F:\DeepMeet\DeepMeet-Guard\server\src\detection_audio"
    #     if os.path.exists(detection_folder):
    #         files = [f for f in os.listdir(detection_folder) if f.endswith('.wav')]
    #         if files:
    #             audio_file = os.path.join(detection_folder, files[0])
    #             print(f"📂 Using existing audio: {files[0]}")
    #         else:
    #             print("❌ No .wav files found in detection_audio/")
    #             print("\n💡 To record audio, run main.py first then:")
    #             print("   curl -X POST http://localhost:8000/api/detection/start")
    #             sys.exit(1)
    #     else:
    #         print("❌ detection_audio folder not found!")
    #         sys.exit(1)
    
 