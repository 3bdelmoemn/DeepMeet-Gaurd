import tensorflow as tf
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def load_and_crop_tf(path):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.crop_to_bounding_box(img, 35, 82, 306, 725)
    return img

def preprocess_efficientnet(image):
    image = tf.cast(image, tf.float32)
    image = tf.keras.applications.efficientnet_v2.preprocess_input(image)
    return image

def convert_audio_to_image(audio_path,saved_path):
    # Mel parameters
    SR = 22050
    N_MELS = 128
    N_FFT = 2048
    HOP_LENGTH = 512

    # =========================
    # LOAD AUDIO
    # =========================
    audio, sr = librosa.load(audio_path, sr=SR)

    # =========================
    # CREATE MEL-SPECTROGRAM
    # =========================
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS
    )

    # Convert to dB
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # =========================
    # SAVE AS IMAGE
    # =========================
    plt.figure(figsize=(10, 4))

    librosa.display.specshow(
        mel_spec_db,
        sr=sr,
        hop_length=HOP_LENGTH,
        x_axis='time',
        y_axis='mel'
    )

    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')
    plt.tight_layout()

    plt.savefig(saved_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    print(f"Saved mel spectrogram image to: {saved_path}")