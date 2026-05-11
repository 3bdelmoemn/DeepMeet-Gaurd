from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter(tags=["cleanup"])


@router.post("/api/cleanup")
async def cleanup():
    import main
    
    # Stop listening
    main.stop_listening = True
    if main.stt_thread and main.stt_thread.is_alive():
        main.stt_thread.join(timeout=3)
    main.stt_thread = None

    # Stop detection
    main.detection_stop_flag = True
    if main.detection_thread and main.detection_thread.is_alive():
        main.detection_thread.join(timeout=3)

    # Clean files
    if main.user_audio_path and os.path.exists(main.user_audio_path):
        try:
            os.remove(main.user_audio_path)
            print(f"🗑️ Deleted audio: {main.user_audio_path}")
        except Exception as e:
            print(f"⚠️ Could not delete audio: {e}")
        main.user_audio_path = None
    
    if main.user_text_path and os.path.exists(main.user_text_path):
        try:
            os.remove(main.user_text_path)
            print(f"🗑️ Deleted text: {main.user_text_path}")
        except Exception as e:
            print(f"⚠️ Could not delete text: {e}")
        main.user_text_path = None

    # Clean assistant
    if main.assistant:
        main.assistant.cleanup()
        main.assistant = None

    with main.state_lock:
        main.last_interviewer_text = ""
        main.last_ai_response = ""

    # Reset flags
    main.stop_listening = False
    main.detection_stop_flag = False

    print("🧹 Cleanup completed")
    return {"status": "success", "message": "Cleanup completed"}


@router.post("/api/stop-listening")
async def stop_listening_endpoint():
    import main
    
    main.stop_listening = True
    if main.stt_thread and main.stt_thread.is_alive():
        main.stt_thread.join(timeout=2)

    return {"status": "success", "message": "Listening stopped"}


@router.get("/api/get-latest")
async def get_latest():
    import main
    
    with main.state_lock:
        data = {
            "interviewer_text": main.last_interviewer_text,
            "ai_response": main.last_ai_response
        }
        main.last_interviewer_text = ""
        main.last_ai_response = ""

    return data