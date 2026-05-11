from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import uvicorn
import json
from datetime import datetime
import threading
import time
from utilities import convert_to_wav
from usecases.interview_assistant_usecase.app import InterViewAssistant
from models.schemas import UserInfo, OrganizationInfo

app = FastAPI(title="DeepMeet Guard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_AUDIO_DIR = "assets/user_voices"
USER_TEXT_DIR = "assets/user_texts"
os.makedirs(USER_AUDIO_DIR, exist_ok=True)
os.makedirs(USER_TEXT_DIR, exist_ok=True)

assistant = None
user_audio_path = None
user_text_path = None
stt_thread = None
stop_listening = False

last_interviewer_text = ""
last_ai_response = ""

state_lock = threading.Lock()


def print_separator(title: str = ""):
    print("\n" + "=" * 60)
    if title:
        print(f"📌 {title}")
    print("=" * 60)


def cleanup_files():
    global user_audio_path, user_text_path
    if user_audio_path and os.path.exists(user_audio_path):
        try:
            os.remove(user_audio_path)
            print(f"🗑️ Deleted audio: {user_audio_path}")
        except Exception as e:
            print(f"⚠️ Could not delete audio: {e}")
        user_audio_path = None
    if user_text_path and os.path.exists(user_text_path):
        try:
            os.remove(user_text_path)
            print(f"🗑️ Deleted text: {user_text_path}")
        except Exception as e:
            print(f"⚠️ Could not delete text: {e}")
        user_text_path = None


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
# ─── Request Models ────────────────────────────────────────────────────────────

class UserInfoRequest(BaseModel):
    name: str = ""
    current_role: str = ""
    years_of_experience: int = 0
    skills: List[str] = []
    experiences: List[Dict[str, str]] = []
    projects: List[Dict[str, str]] = []
    strengths: List[str] = []
    areas_to_improve: List[str] = []

class OrganizationInfoRequest(BaseModel):
    company: str = ""
    industry: str = ""
    tech_stack: str = ""
    role: str = ""
    responsibilities: str = ""

class SetupRequest(BaseModel):
    user_info: UserInfoRequest
    organization_info: OrganizationInfoRequest

class ChatRequest(BaseModel):
    message: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "assistant_ready": assistant is not None,
        "listening_active": stt_thread is not None and stt_thread.is_alive() if stt_thread else False
    }


@app.get("/api/get-latest")
async def get_latest():
    global last_interviewer_text, last_ai_response

    with state_lock:
        data = {
            "interviewer_text": last_interviewer_text,
            "ai_response": last_ai_response
        }
        last_interviewer_text = ""
        last_ai_response = ""

    return JSONResponse(data)


@app.post("/api/cleanup")
async def cleanup():
    global assistant, user_audio_path, user_text_path, stop_listening, stt_thread, last_interviewer_text, last_ai_response

    stop_listening = True
    if stt_thread and stt_thread.is_alive():
        stt_thread.join(timeout=3)
    stt_thread = None

    cleanup_files()

    if assistant:
        assistant.cleanup()
        assistant = None

    with state_lock:
        last_interviewer_text = ""
        last_ai_response = ""

    # Reset flag AFTER thread is confirmed stopped
    stop_listening = False

    print("🧹 Cleanup completed")
    return JSONResponse({"status": "success", "message": "Cleanup completed"})


@app.post("/api/upload-voice")
async def upload_voice(
    audio: UploadFile = File(...),
    reference_text: Optional[str] = Form(None)
):
    global user_audio_path, user_text_path

    print_separator("VOICE UPLOAD RECEIVED")
    print(f"🎤 Audio file: {audio.filename}")

    try:
        cleanup_files()
        timestamp = str(int(datetime.now().timestamp()))
        original_ext = os.path.splitext(audio.filename)[1]
        base_name = os.path.splitext(audio.filename)[0]

        temp_filename = f"{base_name}_{timestamp}{original_ext}"
        temp_path = os.path.join(USER_AUDIO_DIR, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(await audio.read())

        if original_ext.lower() != '.wav':
            try:
                print("🔄 Converting to WAV...")
                wav_path = convert_to_wav(temp_path)
                os.remove(temp_path)
                user_audio_path = wav_path
                print("✅ Converted to WAV")
            except Exception as e:
                print(f"⚠️ Could not convert: {e}")
                user_audio_path = temp_path
        else:
            user_audio_path = temp_path

        if reference_text:
            text_filename = f"{base_name}_{timestamp}.txt"
            text_filepath = os.path.join(USER_TEXT_DIR, text_filename)
            with open(text_filepath, "w", encoding="utf-8") as f:
                f.write(reference_text)
            user_text_path = text_filepath
            print("✅ Text saved")

        return JSONResponse({"status": "success", "message": "Voice uploaded successfully"})

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/setup")
async def setup_interview(request: SetupRequest):
    global assistant, stt_thread, stop_listening

    print_separator("SETUP REQUEST RECEIVED")

    try:
        if not user_audio_path or not os.path.exists(user_audio_path):
            raise HTTPException(status_code=400, detail="Please upload voice first")
        if not user_text_path or not os.path.exists(user_text_path):
            raise HTTPException(status_code=400, detail="Please provide reference text")

        # Build education string from experiences if available
        education_str = "Not provided"
        if request.user_info.experiences:
            first_exp = request.user_info.experiences[0]
            education_str = first_exp.get("education", "Not provided")

        user_info_dict = {
            "name": request.user_info.name,
            "role": request.user_info.current_role,
            "skills": request.user_info.skills,
            "experience": [
                exp.get("description", "") or f"{exp.get('role', '')} at {exp.get('company', '')}"
                for exp in request.user_info.experiences
            ],
            "education": education_str,
            "projects": [
                proj.get("title", "") + ": " + proj.get("description", "")
                for proj in request.user_info.projects
            ],
            "strengths": request.user_info.strengths,
            "weaknesses": request.user_info.areas_to_improve,
        }

        org_info_dict = {
            "company": request.organization_info.company,
            "industry": request.organization_info.industry,
            "tech_stack": [
                tech.strip()
                for tech in request.organization_info.tech_stack.split(",")
            ] if request.organization_info.tech_stack else [],
            "role": request.organization_info.role,
            "responsibilities": [
                resp.strip()
                for resp in request.organization_info.responsibilities.split("\n")
                if resp.strip()
            ] if request.organization_info.responsibilities else [],
        }

        print("\n🔧 Initializing Interview Assistant...")
       
        assistant = InterViewAssistant()
        assistant.setup(
            ref_audio_path=user_audio_path,
            ref_text_content=user_text_path
        )

        user_info = UserInfo(**user_info_dict)
        org_info = OrganizationInfo(**org_info_dict)
        assistant.impersonate(user_info=user_info, organization_info=org_info)
        print(user_info)
        print(org_info)
        print("✅ Setup completed successfully!")
        print("\n🎙️ Starting voice recognition thread...")

        stop_listening = False
        stt_thread = threading.Thread(target=start_continuous_listening, daemon=True)
        stt_thread.start()

        print("✅ Voice recognition active!")

        return JSONResponse({
            "status": "success",
            "message": "Setup complete. Voice recognition active."
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    global assistant

    if assistant is None:
        raise HTTPException(status_code=400, detail="Assistant not initialized")

    try:
        response = assistant.llm.generate_response(request.message)
        assistant.tts.speak(response)
        return JSONResponse({
            "response": response,
            "threat_score": getattr(assistant, 'threat_score', 0)
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stop-listening")
async def stop_listening_endpoint():
    global stop_listening, stt_thread

    stop_listening = True
    if stt_thread and stt_thread.is_alive():
        stt_thread.join(timeout=2)

    return JSONResponse({"status": "success", "message": "Listening stopped"})


import logging
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.disabled = True
logging.getLogger("uvicorn").setLevel(logging.WARNING)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 DeepMeet Guard API Server")
    print("=" * 60)
    print("Server: http://localhost:8000")
    print("Docs:   http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)