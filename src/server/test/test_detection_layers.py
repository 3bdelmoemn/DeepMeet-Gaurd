from ..controllers.fake_audio_detection_controller import FakeAudioDetectionController
import warnings
import logging
import os
from tqdm import  tqdm
import pprint
# إخفاء torch distributed warning
logging.getLogger("torch.distributed.elastic").setLevel(logging.ERROR)

# إخفاء transformers warnings
logging.getLogger("transformers").setLevel(logging.ERROR)


# إخفاء tqdm progress bars
os.environ["TQDM_DISABLE"] = "1"

detector=FakeAudioDetectionController()
TEST_SAMPLES_DIR=r"D:\Education\GraduationProject\last version\DeepMeet-Gaurd\src\assets\test_samples"

if __name__=="__main__":
    if detector.setup():
        for path in tqdm(os.listdir(TEST_SAMPLES_DIR)):
            res=detector.predict(os.path.join(TEST_SAMPLES_DIR, path),return_layer_results=True)
            print("-"*50)
            pprint.pprint(f"Results for {path}: {res}")
            print("-"*50)
        print("All models loaded successfully")
    else:
        print("Failed to load one or more models")





