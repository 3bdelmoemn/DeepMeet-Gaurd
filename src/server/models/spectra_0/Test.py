import torch
import librosa
import numpy as np
from model import Spectra0Model as Model 

# 1. Add this tool designed specifically for reading .safetensors files
from safetensors.torch import load_file 

model = Model()

# 2. Replace torch.load with load_file
state_dict = load_file("model.safetensors", device="cpu")
model.load_state_dict(state_dict)

model.eval()

def predict(file):
    audio, sr = librosa.load(file, sr=16000)
    audio = torch.tensor(audio).unsqueeze(0)
    
    with torch.no_grad():
        out = model(audio)
        score = torch.softmax(out, dim=1)
        
    pred = torch.argmax(score).item()
    return pred
import sys # ضيف دي لو مش موجودة فوق

# الكود ده بيستقبل المسار اللي جاي من السيرفر (من subprocess)
if len(sys.argv) > 1:
    target_file = sys.argv[1]
else:
    # لو مفيش مسار مبعوت، هيستخدم ده كاحتياطي
    target_file = r"C:\Users\Panda\Desktop\Recording.wav"

result = predict(target_file)
# مهم جداً نطبع النتيجة بس (رقم 0 أو 1) عشان السيرفر يعرف يقرأها صح
print(result)
# 0 0 0 1 1 1 