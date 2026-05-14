from server.services import detector
import warnings
import logging
import os
from tqdm import  tqdm
import pprint
logging.getLogger("torch.distributed.elastic").setLevel(logging.ERROR)

logging.getLogger("transformers").setLevel(logging.ERROR)


os.environ["TQDM_DISABLE"] = "1"


TEST_SAMPLES_DIR=r"server/test/test_samples"

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





