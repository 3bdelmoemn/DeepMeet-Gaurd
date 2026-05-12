# F:\DeepMeet\DeepMeet-Guard\server\src\models\behave_live\voice_deepfake.py

import numpy as np
import librosa
import joblib
import os
from scipy import stats
from scipy.spatial.distance import cosine, euclidean
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')
import matplotlib
matplotlib.use('Agg')

# ============================================================
# 1. Advanced Feature Extractor (كاملاً)
# ============================================================

class AdvancedFeatureExtractor:
    def __init__(self, sr=16000):
        self.sr = sr
        self.MIN_DURATION_SEC = 3.0

    @staticmethod
    def _sigmoid(x, center, scale=1.0):
        return float(1 / (1 + np.exp(-scale * (x - center))))

    def _detect_breath_score(self, audio, frame_length=2048, hop_length=512):
        energy = np.array([
            np.sum(audio[i:i + frame_length] ** 2)
            for i in range(0, len(audio) - frame_length, hop_length)
        ])
        if len(energy) == 0:
            return 0.0
        threshold = np.median(energy) * 0.15
        breath_ratio = np.sum(energy < threshold) / len(energy)
        return self._sigmoid(breath_ratio, center=0.15, scale=20.0)

    def _pause_variance_score(self, audio):
        intervals = librosa.effects.split(audio, top_db=30)
        if len(intervals) < 2:
            return 0.0
        pauses = [intervals[i][0] - intervals[i-1][1] for i in range(1, len(intervals))]
        pauses = [p for p in pauses if p > 0]
        if not pauses:
            return 0.0
        mean_p = np.mean(pauses)
        if mean_p == 0:
            return 0.0
        cv = np.std(pauses) / mean_p
        return float(min(cv / 2.0, 1.0))

    def _spectral_variation_score(self, audio):
        mel = librosa.feature.melspectrogram(y=audio, sr=self.sr, n_mels=64)
        log_mel = librosa.power_to_db(mel)
        diff = np.diff(log_mel, axis=1)
        variation = np.var(diff)
        return float(self._sigmoid(variation, center=15, scale=0.15))

    def _mfcc_naturalness_score(self, audio):
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=20)
        temporal_var = np.mean(np.var(mfccs, axis=1))
        return float(self._sigmoid(temporal_var, center=150, scale=0.02))

    def _pitch_irregularity_score(self, audio):
        f0, voiced_flag, _ = librosa.pyin(
            audio, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'), sr=self.sr
        )
        f0_voiced = f0[voiced_flag & ~np.isnan(f0)]
        if len(f0_voiced) < 10:
            return 0.0
        jitter = np.mean(np.abs(np.diff(f0_voiced))) / (np.mean(f0_voiced) + 1e-6)
        return self._sigmoid(jitter, center=0.05, scale=40.0)

    def _spectral_flatness_score(self, audio):
        flatness = librosa.feature.spectral_flatness(y=audio)
        mean_flatness = float(np.mean(flatness))
        return float(min(mean_flatness * 200, 1.0))

    def _zcr_variation_score(self, audio):
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        zcr_var = np.var(zcr)
        return self._sigmoid(zcr_var, center=0.005, scale=500)

    def _delta_mfcc_score(self, audio):
        mfccs = librosa.feature.mfcc(y=audio, sr=self.sr, n_mfcc=20)
        delta = librosa.feature.delta(mfccs)
        delta2 = librosa.feature.delta(mfccs, order=2)
        score = np.mean(np.var(delta, axis=1)) + 0.5 * np.mean(np.var(delta2, axis=1))
        return self._sigmoid(score, center=40.0, scale=0.05)

    def _hnr_score(self, audio):
        harmonics, percussive = librosa.effects.hpss(audio)
        harmonic_energy = np.mean(harmonics ** 2) + 1e-10
        noise_energy = np.mean(percussive ** 2) + 1e-10
        hnr_db = 10 * np.log10(harmonic_energy / noise_energy)
        return self._sigmoid(hnr_db, center=12.0, scale=-0.3)

    def extract_all_features(self, audio_path):
        """Extract all features from audio file"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sr)
        except Exception as e:
            print(f"Error loading {audio_path}: {e}")
            return None
        
        duration = len(y) / sr
        if duration < self.MIN_DURATION_SEC:
            print(f"Audio too short: {duration:.2f}s (min {self.MIN_DURATION_SEC}s)")
            return None
        
        features = {}
        
        # ========== 1. RMS Features ==========
        try:
            rms = librosa.feature.rms(y=y, frame_length=512, hop_length=256)[0]
            features['rms_cv'] = np.std(rms) / (np.mean(rms) + 1e-8)
            features['rms_std'] = np.std(rms)
            features['rms_entropy'] = stats.entropy(np.histogram(rms, bins=20)[0] + 1e-8)
            features['energy_skewness'] = stats.skew(rms)
            features['energy_kurtosis'] = stats.kurtosis(rms)
        except:
            for k in ['rms_cv', 'rms_std', 'rms_entropy', 'energy_skewness', 'energy_kurtosis']:
                features[k] = 0

        # ========== 2. Pitch Features ==========
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[pitches > 0]
            if len(pitch_values) > 5:
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
                features['pitch_cv'] = np.std(pitch_values) / (np.mean(pitch_values) + 1e-8)
                features['pitch_range'] = np.max(pitch_values) - np.min(pitch_values)
                features['pitch_entropy'] = stats.entropy(np.histogram(pitch_values, bins=20)[0] + 1e-8)
                pitch_changes = np.diff(pitch_values)
                if len(pitch_changes) > 1:
                    features['pitch_change_mean'] = np.mean(np.abs(pitch_changes))
                    features['pitch_change_std'] = np.std(pitch_changes)
                else:
                    features['pitch_change_mean'] = 0
                    features['pitch_change_std'] = 0
                features['jitter_local'] = np.std(pitch_values) / (np.mean(pitch_values) + 1e-8)
                if len(pitch_values) > 3:
                    rap_values = [abs(pitch_values[i] - (pitch_values[i-1] + pitch_values[i+1])/2)
                                 for i in range(1, len(pitch_values)-1)]
                    features['jitter_rap'] = np.mean(rap_values) / (np.mean(pitch_values) + 1e-8) if rap_values else 0
                else:
                    features['jitter_rap'] = 0
                rms_values = rms[rms > 1e-8]
                if len(rms_values) > 5:
                    features['shimmer_local'] = np.std(rms_values) / (np.mean(rms_values) + 1e-8)
                else:
                    features['shimmer_local'] = 0
            else:
                for k in ['pitch_mean', 'pitch_std', 'pitch_cv', 'pitch_range', 'pitch_entropy',
                          'pitch_change_mean', 'pitch_change_std', 'jitter_local', 'jitter_rap', 'shimmer_local']:
                    features[k] = 0
        except:
            for k in ['pitch_mean', 'pitch_std', 'pitch_cv', 'pitch_range', 'pitch_entropy',
                      'pitch_change_mean', 'pitch_change_std', 'jitter_local', 'jitter_rap', 'shimmer_local']:
                features[k] = 0

        # ========== 3. Silence Features ==========
        try:
            silence_mask = np.abs(y) < 0.01
            features['silence_ratio'] = np.sum(silence_mask) / len(y)
            features['transition_rate'] = np.sum(np.diff(silence_mask.astype(int)) != 0) / duration
            features['silence_count'] = len(find_peaks(silence_mask.astype(float))[0])
            silent_segments = []
            in_silence = False
            start = 0
            for i, s in enumerate(silence_mask):
                if s and not in_silence:
                    start = i
                    in_silence = True
                elif not s and in_silence:
                    silent_segments.append(i - start)
                    in_silence = False
            if silent_segments:
                pause_durations = np.array(silent_segments) / sr
                features['pause_duration_mean'] = np.mean(pause_durations)
                features['pause_duration_std'] = np.std(pause_durations)
                features['pause_duration_cv'] = np.std(pause_durations) / (np.mean(pause_durations) + 1e-8)
            else:
                for k in ['pause_duration_mean', 'pause_duration_std', 'pause_duration_cv']:
                    features[k] = 0
        except:
            for k in ['silence_ratio', 'transition_rate', 'silence_count', 'pause_duration_mean', 'pause_duration_std', 'pause_duration_cv']:
                features[k] = 0

        # ========== 4. Spectral Features ==========
        try:
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            features['spectral_centroid_cv'] = np.std(spectral_centroids) / (np.mean(spectral_centroids) + 1e-8)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            features['spectral_rolloff_std'] = np.std(spectral_rolloff)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
            features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            features['zcr_cv'] = np.std(zcr) / (np.mean(zcr) + 1e-8)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features['spectral_contrast_mean'] = np.mean(spectral_contrast)
            features['spectral_contrast_std'] = np.std(spectral_contrast)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            features['spectral_flatness_mean'] = np.mean(spectral_flatness)
            features['spectral_flatness_std'] = np.std(spectral_flatness)
        except:
            pass

        # ========== 5. MFCC Features ==========
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            mfcc_delta = librosa.feature.delta(mfccs)
            features['mfcc_delta_mean'] = np.mean(mfcc_delta)
            features['mfcc_delta_std'] = np.std(mfcc_delta)
        except:
            pass

        # ========== 6. Phase Features ==========
        try:
            stft = librosa.stft(y)
            phase = np.angle(stft)
            magnitude = np.abs(stft)
            phase_diff = np.diff(phase, axis=1)
            features['phase_consistency'] = np.mean(np.abs(phase_diff))
            features['magnitude_flatness'] = np.exp(np.mean(np.log(magnitude + 1e-8))) / (np.mean(magnitude) + 1e-8)
        except:
            features['phase_consistency'] = 0
            features['magnitude_flatness'] = 0

        # ========== 7. Behavioral Features ==========
        try:
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_peaks = find_peaks(onset_env)[0]
            if len(onset_peaks) > 1:
                intervals = np.diff(onset_peaks) / sr
                features['rate_variation_cv'] = np.std(intervals) / (np.mean(intervals) + 1e-8)
            else:
                features['rate_variation_cv'] = 0
            speech_segments = []
            in_speech = False
            start = 0
            for i, s in enumerate(~silence_mask):
                if s and not in_speech:
                    start = i
                    in_speech = True
                elif not s and in_speech:
                    speech_segments.append(i - start)
                    in_speech = False
            if speech_segments:
                speech_durations = np.array(speech_segments) / sr
                features['speech_segment_cv'] = np.std(speech_durations) / (np.mean(speech_durations) + 1e-8)
            else:
                features['speech_segment_cv'] = 0
        except:
            features['rate_variation_cv'] = 0
            features['speech_segment_cv'] = 0

        # ========== 8. Metadata ==========
        features['duration'] = duration

        # ========== 9. Liveness Features ==========
        try:
            y_norm = y / (np.max(np.abs(y)) + 1e-10)
            breath = self._detect_breath_score(y_norm)
            pause_var = self._pause_variance_score(y_norm)
            spectral_var = self._spectral_variation_score(y_norm)
            mfcc_nat = self._mfcc_naturalness_score(y_norm)
            pitch_irr = self._pitch_irregularity_score(y_norm)
            spec_flat = self._spectral_flatness_score(y_norm)
            zcr_var = self._zcr_variation_score(y_norm)
            delta_mfcc = self._delta_mfcc_score(y_norm)
            hnr = self._hnr_score(y_norm)
            
            liveness_score = (
                0.10 * breath + 0.08 * pause_var + 0.12 * spectral_var + 0.12 * mfcc_nat +
                0.15 * pitch_irr + 0.08 * spec_flat + 0.08 * zcr_var + 0.13 * delta_mfcc + 0.14 * hnr
            )
            
            features['liveness_breath_score'] = round(breath, 4)
            features['liveness_pause_variance_score'] = round(pause_var, 4)
            features['liveness_spectral_variation_score'] = round(spectral_var, 4)
            features['liveness_mfcc_naturalness_score'] = round(mfcc_nat, 4)
            features['liveness_pitch_irregularity_score'] = round(pitch_irr, 4)
            features['liveness_spectral_flatness_score'] = round(spec_flat, 4)
            features['liveness_zcr_variation_score'] = round(zcr_var, 4)
            features['liveness_delta_mfcc_score'] = round(delta_mfcc, 4)
            features['liveness_hnr_score'] = round(hnr, 4)
            features['liveness_score_total'] = round(float(liveness_score), 4)
        except Exception as e:
            print(f"⚠️ Error in liveness features: {e}")

        return features


# ============================================================
# 2. VoiceDeepfakeDetector (كاملاً)
# ============================================================

class VoiceDeepfakeDetector:
    def __init__(self, model_dir=None):
        """
        model_dir: المسار إلى المجلد اللي فيه الملفات (pkl, npy)
        لو مش متحدد، هنستخدم المجلد الحالي
        """
        print("⚙️ Loading BehaveLive Deepfake Detector...")
        
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        
        model_path = os.path.join(model_dir, "final_model_package.pkl")
        pool_mean_path = os.path.join(model_dir, "pool_mean.npy")
        pool_matrix_path = os.path.join(model_dir, "pool_matrix.npy")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model file not found at: {model_path}")
        
        self.model_package = joblib.load(model_path)
        self.pool_mean = np.load(pool_mean_path)
        self.pool_matrix = np.load(pool_matrix_path)
        self.extractor = AdvancedFeatureExtractor()
        
        print("✅ BehaveLive Detector Ready!")

    def _compute_distance_features(self, features_dict, top_k=10):
        """Compute cosine and euclidean distances against bonafide pool"""
        if not features_dict:
            return None

        feature_values = list(features_dict.values())

        if len(feature_values) >= len(self.pool_mean):
            feature_vector = np.array(feature_values[:len(self.pool_mean)], dtype=np.float64)
        else:
            feature_vector = np.zeros(len(self.pool_mean), dtype=np.float64)
            feature_vector[:len(feature_values)] = feature_values[:len(feature_values)]

        pool_mean_clean = np.array([0 if (np.isnan(x) or np.isinf(x)) else x for x in self.pool_mean], dtype=np.float64)
        feature_vector_clean = np.array([0 if (np.isnan(x) or np.isinf(x)) else x for x in feature_vector], dtype=np.float64)

        try:
            cos_dist = cosine(feature_vector_clean, pool_mean_clean)
        except:
            cos_dist = 1.0

        try:
            euc_dist = euclidean(feature_vector_clean, pool_mean_clean)
        except:
            euc_dist = 1000.0

        min_cos, min_euc, all_cos = 1.0, float('inf'), []

        for pool_vec in self.pool_matrix:
            pool_vec_clean = np.array([0 if (np.isnan(x) or np.isinf(x)) else x for x in pool_vec], dtype=np.float64)
            try:
                c = cosine(feature_vector_clean, pool_vec_clean)
                e = euclidean(feature_vector_clean, pool_vec_clean)
                all_cos.append(c)
                if c < min_cos: min_cos = c
                if e < min_euc: min_euc = e
            except:
                continue

        k_avg = np.mean(sorted(all_cos)[:min(top_k, len(all_cos))]) if all_cos else 1.0

        return {
            'cosine_to_mean': float(cos_dist),
            'euclidean_to_mean': float(euc_dist),
            'min_cosine': float(min_cos),
            'min_euclidean': float(min_euc),
            'avg_topk_cosine': float(k_avg)
        }

    def preprocess(self, audio_path):
        """Preprocess audio and extract features for model input"""
        feats = self.extractor.extract_all_features(audio_path)
        if not feats:
            raise ValueError("❌ Failed to extract basic features from the audio.")

        dist_feats = self._compute_distance_features(feats)
        if not dist_feats:
            raise ValueError("❌ Failed to compute distance features.")

        combined_all_feats = {**feats, **dist_feats}

        feature_vector = []
        for feat_name in self.model_package['feature_names']:
            feature_vector.append(combined_all_feats.get(feat_name, 0.0))

        X_new = np.array(feature_vector).reshape(1, -1)
        X_new_scaled = self.model_package['scaler'].transform(X_new)

        # Add noise like in training
        np.random.seed(42)
        X_new_noisy = X_new_scaled + np.random.normal(0, 0.03, X_new_scaled.shape)

        return X_new_noisy

    def detect(self, audio_path):
        """
        Detect if audio is AI-generated or Human
        Returns: dict with status, prediction, ai_probability, human_probability, confidence
        """
        try:
            X_ready = self.preprocess(audio_path)
            prob = self.model_package['ensemble'].predict_proba(X_ready)[0, 1]
            threshold = self.model_package['threshold']

            is_ai = int(prob >= threshold)

            return {
                'status': 'success',
                'prediction': 'AI' if is_ai == 1 else 'HUMAN',
                'ai_probability': round(prob, 4),
                'human_probability': round(1 - prob, 4),
                'confidence': round(max(prob, 1 - prob), 4)
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }