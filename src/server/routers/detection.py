from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from server.utilities import (
    create_meeting_session,
    capture_speaker_audio,
    run_period_detection,
    save_period_results,
    get_meeting_report,
    _get_meeting_dir,
    _get_period_dir,
)
from server.helpers import get_config
import threading
import logging
import numpy as np
import os
import json
import librosa

settings = get_config()
logger   = logging.getLogger('uvicorn.error')

router = APIRouter(tags=["Detector"], prefix="/deepmeet/detector")


# ============================================================
# Start Detection
# ============================================================
@router.post("/start")
async def start_detection(meeting_name: str, request: Request):
    detector = request.app.state.detector

    if getattr(request.app.state, "detection_active", False):
        raise HTTPException(status_code=409, detail="Detection already running")

    try:
        meeting_dir = create_meeting_session(meeting_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create meeting session: {e}")

    # Shared event for clean cancellation
    stop_event = threading.Event()
    request.app.state.detection_stop_event = stop_event

    def _detection_loop():
        request.app.state.detection_active   = True
        request.app.state.detection_meeting  = meeting_dir
        period_num = 1

        try:
            while not stop_event.is_set():
                logger.info(f"📍 Starting period {period_num}...")

                try:
                    saved_files = capture_speaker_audio(
                        meeting_dir=meeting_dir,
                        period_num=period_num,
                        max_duration=settings.DETECTOR_MAX_DURATION,
                    )
                except Exception as e:
                    logger.error(f"❌ Capture failed period {period_num}: {e}")
                    break

                period_dir = _get_period_dir(meeting_dir, period_num)
                results    = run_period_detection(detector, period_dir, period_num)
                save_period_results(meeting_dir, period_num, results)
                period_num += 1

                logger.info(f"⏳ Waiting {settings.DETECTOR_PERIOD_INTERVAL}s for next period...")
                # Single Event.wait() — signals instantly when stop_event is set
                if stop_event.wait(timeout=settings.DETECTOR_PERIOD_INTERVAL):
                    break

        except Exception as e:
            logger.error(f"❌ Detection loop error: {e}")
        finally:
            request.app.state.detection_active = False
            logger.info("🛑 Detection loop stopped.")

    thread = threading.Thread(target=_detection_loop, daemon=True, name=f"detection-{meeting_name}")
    request.app.state.detection_thread = thread
    thread.start()

    logger.info(f"✅ Detection started for meeting: {meeting_name}")
    return JSONResponse({
        "status":       "success",
        "message":      "Detection started",
        "meeting_name": meeting_name,
    })


# ============================================================
# End Detection
# ============================================================
@router.post("/end")
async def end_detection(request: Request):
    if not getattr(request.app.state, "detection_active", False):
        raise HTTPException(status_code=409, detail="No detection is running")

    # Signal the detection loop to stop
    stop_event: threading.Event = getattr(request.app.state, "detection_stop_event", None)
    if stop_event:
        stop_event.set()
    request.app.state.detection_active = False

    thread: threading.Thread = getattr(request.app.state, "detection_thread", None)
    if thread:
        thread.join(timeout=15)
        if thread.is_alive():
            logger.warning("⚠️ Detection thread did not stop within timeout — may be a zombie")
        request.app.state.detection_thread = None
    request.app.state.detection_stop_event = None

    logger.info("✅ Detection stopped.")
    return JSONResponse({
        "status":  "success",
        "message": "Detection stopped",
    })


# ============================================================
# Report
# ============================================================
@router.get("/report")
async def detection_report(meeting_name: str, request: Request):
    try:
        meeting_dir = _get_meeting_dir(meeting_name)
        report      = get_meeting_report(meeting_dir)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No results found for: {meeting_name}")
    except Exception as e:
        logger.error(f"❌ Report failed [{meeting_name}]: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

    return JSONResponse({
        "status": "success",
        "report": report,
    })


# ============================================================
# RICH ANALYSIS — ALL REAL, NO MOCK
# ============================================================

def _extract_real_waveform(audio_dir: str, period: int, num_points: int = 300) -> list[float]:
    """Extract REAL waveform from recorded audio file"""
    period_dir = os.path.join(audio_dir, f"period_{period}")
    if not os.path.exists(period_dir):
        logger.warning(f"⚠️ Period dir not found: {period_dir}")
        return []
    
    audio_files = [f for f in os.listdir(period_dir) if f.endswith('.wav')]
    if not audio_files:
        logger.warning(f"⚠️ No audio files found in {period_dir}")
        return []
    
    audio_path = os.path.join(period_dir, audio_files[0])
    
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        if len(y) > num_points:
            step = len(y) // num_points
            waveform = y[::step][:num_points]
        else:
            if len(y) < num_points:
                waveform = np.pad(y, (0, num_points - len(y)), 'constant')
            else:
                waveform = y[:num_points]
        
        max_val = np.max(np.abs(waveform))
        if max_val > 0:
            waveform = waveform / max_val
        
        return waveform.tolist()
    except Exception as e:
        logger.error(f"❌ Failed to extract waveform from {audio_path}: {e}")
        return []


def _extract_real_spectrogram(audio_dir: str, period: int, freq_bins: int = 32, time_bins: int = 64) -> list[list[float]]:
    """Extract REAL spectrogram from recorded audio file"""
    period_dir = os.path.join(audio_dir, f"period_{period}")
    if not os.path.exists(period_dir):
        logger.warning(f"⚠️ Period dir not found: {period_dir}")
        return []
    
    audio_files = [f for f in os.listdir(period_dir) if f.endswith('.wav')]
    if not audio_files:
        logger.warning(f"⚠️ No audio files found in {period_dir}")
        return []
    
    audio_path = os.path.join(period_dir, audio_files[0])
    
    try:
        y, sr = librosa.load(audio_path, sr=16000)
        
        D = librosa.stft(y, n_fft=512, hop_length=256)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        freq_bins_actual = S_db.shape[0]
        time_bins_actual = S_db.shape[1]
        
        if freq_bins_actual > freq_bins:
            freq_step = freq_bins_actual // freq_bins
            S_db = S_db[::freq_step, :]
        else:
            pad = freq_bins - freq_bins_actual
            S_db = np.pad(S_db, ((0, pad), (0, 0)), 'constant', constant_values=-80)
        
        if time_bins_actual > time_bins:
            time_step = time_bins_actual // time_bins
            S_db = S_db[:, ::time_step]
        else:
            pad = time_bins - time_bins_actual
            S_db = np.pad(S_db, ((0, 0), (0, pad)), 'constant', constant_values=-80)
        
        S_db = S_db[:freq_bins, :time_bins]
        
        min_val = np.min(S_db)
        max_val = np.max(S_db)
        if max_val - min_val > 0:
            S_db = (S_db - min_val) / (max_val - min_val)
        else:
            S_db = np.zeros_like(S_db)
        
        return S_db.tolist()
    except Exception as e:
        logger.error(f"❌ Failed to extract spectrogram from {audio_path}: {e}")
        return []


def _extract_real_stats(waveform: list[float]) -> dict:
    """Calculate REAL stats from waveform"""
    if not waveform:
        return {"rms": 0, "zcr_rate": 0, "spectral_flatness": 0, "silence_ratio": 0, "peak_variance": 0}
    
    arr = np.array(waveform)
    n = len(arr)
    
    rms = float(np.sqrt(np.mean(arr ** 2)))
    
    zero_crossings = int(np.sum(np.diff(np.sign(arr)) != 0))
    zcr_rate = round(zero_crossings / n, 4)
    
    abs_arr = np.abs(arr) + 1e-10
    geo_mean = float(np.exp(np.mean(np.log(abs_arr))))
    arith_mean = float(np.mean(abs_arr))
    spectral_flatness = round(geo_mean / arith_mean, 4) if arith_mean > 0 else 0
    
    threshold = 0.03
    silence_ratio = round(float(np.mean(np.abs(arr) < threshold)), 4)
    
    peaks = arr[np.where(np.diff(np.sign(np.diff(arr))) < 0)[0]]
    peak_variance = round(float(np.var(peaks)) if len(peaks) > 1 else 0.0, 6)
    
    return {
        "rms": round(rms, 4),
        "zcr_rate": zcr_rate,
        "spectral_flatness": spectral_flatness,
        "silence_ratio": silence_ratio,
        "peak_variance": peak_variance,
    }


def _extract_real_anomaly_markers(waveform: list[float], is_fake: bool) -> list[dict]:
    """Extract REAL anomaly markers from waveform for fake audio"""
    if not is_fake or not waveform:
        return []
    
    arr = np.array(waveform)
    n = len(arr)
    markers = []
    
    # Find unnatural silent gaps
    for i in range(20, n - 20):
        window = 8
        local_avg = np.mean(np.abs(arr[max(0, i-window):min(n, i+window)]))
        
        if local_avg < 0.01:
            surrounding_avg = np.mean(np.abs(arr[max(0, i-30):min(n, i-10)])) + np.mean(np.abs(arr[max(0, i+10):min(n, i+30)]))
            if surrounding_avg > 0.05:
                markers.append({
                    "position": i,
                    "type": "silent_gap",
                    "label": "Unnatural Silence",
                    "severity": "high" if surrounding_avg > 0.1 else "medium"
                })
                i += 30
    
    # Find uniform noise regions (TTS artifacts)
    for i in range(40, n - 40):
        window = 15
        segment = arr[max(0, i-window):min(n, i+window)]
        if len(segment) > 5:
            variance = np.var(segment)
            if 0.0001 < variance < 0.001:
                markers.append({
                    "position": i,
                    "type": "uniform_noise",
                    "label": "TTS Artifact",
                    "severity": "medium"
                })
                i += 40
    
    # Find regular patterns (synthetic consistency)
    for i in range(60, n - 60):
        window = 20
        segment = arr[max(0, i-window):min(n, i+window)]
        if len(segment) > 5:
            autocorr = np.correlate(segment, segment, mode='full')
            autocorr = autocorr / np.max(autocorr)
            if len(autocorr) > 10 and np.max(autocorr[5:15]) > 0.8:
                markers.append({
                    "position": i,
                    "type": "synthetic_pattern",
                    "label": "Regular Pattern",
                    "severity": "low"
                })
                i += 50
    
    return markers[:4]


# ============================================================
# ANALYSIS ENDPOINT — ALL REAL DATA
# ============================================================
@router.get("/analysis")
async def rich_analysis(meeting_name: str, request: Request):
    """
    Returns REAL data only:
    - waveform points from actual audio
    - spectrogram from actual audio
    - signal statistics from actual audio
    - anomaly markers from actual audio (if fake)
    - per-layer breakdown from actual detection results
    """
    try:
        meeting_dir = _get_meeting_dir(meeting_name)
        report = get_meeting_report(meeting_dir)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No results found for: {meeting_name}")
    except Exception as e:
        logger.error(f"Report failed [{meeting_name}]: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    audio_dir = meeting_dir

    periods_analysis = []
    for period in report.get("periods", []):
        is_fake_period = period["fake_count"] > period["real_count"]

        # Extract REAL waveform
        waveform = _extract_real_waveform(audio_dir, period["period"], num_points=300)
        
        # If no real waveform found, skip this period (no mock fallback)
        if not waveform:
            logger.warning(f"No real waveform for period {period['period']}, skipping")
            continue
        
        stats = _extract_real_stats(waveform)
        markers = _extract_real_anomaly_markers(waveform, is_fake_period)
        
        # Extract REAL spectrogram
        spectrogram = _extract_real_spectrogram(audio_dir, period["period"], freq_bins=32, time_bins=64)
        
        # If no real spectrogram, skip (no mock fallback)
        if not spectrogram:
            logger.warning(f"No real spectrogram for period {period['period']}, skipping")
            continue

        # Per-sample layer breakdown from actual detection results
        samples_detail = []
        for sample in period.get("samples", []):
            result = sample.get("result", {})
            layers = result.get("layers", [])
            samples_detail.append({
                "sample": sample.get("sample", ""),
                "prediction": result.get("prediction", "Unknown"),
                "confidence": result.get("confidence", "N/A"),
                "layers": [
                    {
                        "name": l.get("layer", ""),
                        "label": "Fake" if l.get("label", 0) == 1 else "Real",
                        "weight": l.get("weight", 0),
                    }
                    for l in layers
                ],
            })

        periods_analysis.append({
            "period": period["period"],
            "timestamp": period["timestamp"],
            "total": period["total"],
            "fake_count": period["fake_count"],
            "real_count": period["real_count"],
            "verdict": "Fake" if is_fake_period else "Real",
            "waveform": waveform,
            "spectrogram": spectrogram,
            "signal_stats": stats,
            "anomaly_markers": markers,
            "samples": samples_detail,
        })

    # Layer-level summary from actual detection results
    layer_totals: dict[str, dict] = {}
    for period in report.get("periods", []):
        for sample in period.get("samples", []):
            layers = sample.get("result", {}).get("layers", [])
            for l in layers:
                name = l.get("layer", "unknown")
                if name not in layer_totals:
                    layer_totals[name] = {"fake": 0, "real": 0, "weight": l.get("weight", 0)}
                if l.get("label", 0) == 1:
                    layer_totals[name]["fake"] += 1
                else:
                    layer_totals[name]["real"] += 1

    layer_summary = [
        {
            "name": name,
            "weight": vals["weight"],
            "total": vals["fake"] + vals["real"],
            "fake_count": vals["fake"],
            "real_count": vals["real"],
            "fake_pct": round(vals["fake"] / (vals["fake"] + vals["real"]) * 100, 1)
                         if (vals["fake"] + vals["real"]) > 0 else 0,
        }
        for name, vals in layer_totals.items()
    ]

    return JSONResponse({
        "status": "success",
        "meeting": report["meeting"],
        "verdict": report["verdict"],
        "total_samples": report["total_samples"],
        "total_fake": report["total_fake"],
        "total_real": report["total_real"],
        "fake_percentage": report["fake_percentage"],
        "layer_summary": layer_summary,
        "periods": periods_analysis,
    })