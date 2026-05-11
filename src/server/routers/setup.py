from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import threading
from datetime import datetime
from utilities import convert_to_wav
from usecases.interview_assistant_usecase.app import InterViewAssistant
from models.schemas import UserInfo, OrganizationInfo

router = APIRouter(tags=["setup"])


def print_separator(title: str = ""):
    print("\n" + "=" * 60)
    if title:
        print(f"📌 {title}")
    print("=" * 60)


def cleanup_files():
    from main import user_audio_path, user_text_path, detection_stop_flag, detection_thread
    
    if user_audio_path and os.path.exists(user_audio_path):
        try:
            os.remove(user_audio_path)
            print(f"🗑️ Deleted audio: {user_audio_path}")
        except Exception as e:
            print(f"⚠️ Could not delete audio: {e}")
        # تعديل الـ global variable
        # هنستخدم main لضبط القيمة
        import main
        main.user_audio_path = None
    
    if user_text_path and os.path.exists(user_text_path):
        try:
            os.remove(user_text_path)
            print(f"🗑️ Deleted text: {user_text_path}")
        except Exception as e:
            print(f"⚠️ Could not delete text: {e}")
        import main
        main.user_text_path = None
    
    detection_stop_flag = True
    if detection_thread and detection_thread.is_alive():
        detection_thread.join(timeout=2)


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


@router.post("/api/upload-voice")
async def upload_voice(
    audio: UploadFile = File(...),
    reference_text: Optional[str] = Form(None)
):
    import main  # استيراد داخل الدالة
    
    print_separator("VOICE UPLOAD RECEIVED")
    print(f"🎤 Audio file: {audio.filename}")

    try:
        cleanup_files()
        timestamp = str(int(datetime.now().timestamp()))
        original_ext = os.path.splitext(audio.filename)[1]
        base_name = os.path.splitext(audio.filename)[0]

        temp_filename = f"{base_name}_{timestamp}{original_ext}"
        temp_path = os.path.join("assets/user_voices", temp_filename)

        with open(temp_path, "wb") as f:
            f.write(await audio.read())

        if original_ext.lower() != '.wav':
            try:
                print("🔄 Converting to WAV...")
                wav_path = convert_to_wav(temp_path)
                os.remove(temp_path)
                main.user_audio_path = wav_path
                print("✅ Converted to WAV")
            except Exception as e:
                print(f"⚠️ Could not convert: {e}")
                main.user_audio_path = temp_path
        else:
            main.user_audio_path = temp_path

        if reference_text:
            text_filename = f"{base_name}_{timestamp}.txt"
            text_filepath = os.path.join("assets/user_texts", text_filename)
            with open(text_filepath, "w", encoding="utf-8") as f:
                f.write(reference_text)
            main.user_text_path = text_filepath
            print("✅ Text saved")

        return JSONResponse({"status": "success", "message": "Voice uploaded successfully"})

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/setup")
async def setup_interview(request: SetupRequest):
    import main  # استيراد داخل الدالة
    
    print_separator("SETUP REQUEST RECEIVED")

    try:
        if not main.user_audio_path or not os.path.exists(main.user_audio_path):
            raise HTTPException(status_code=400, detail="Please upload voice first")
        if not main.user_text_path or not os.path.exists(main.user_text_path):
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

        main.assistant = InterViewAssistant()
        main.assistant.setup(
            ref_audio_path=main.user_audio_path,
            ref_text_content=main.user_text_path
        )

        user_info = UserInfo(**user_info_dict)
        org_info = OrganizationInfo(**org_info_dict)
        main.assistant.impersonate(user_info=user_info, organization_info=org_info)

        main.detection_stop_flag = False
        if main.detection_thread is None or not main.detection_thread.is_alive():
            main.detection_thread = main.start_periodic_detection()
            print("🔍 Speaker detection active (every 60s)")

        print("✅ Setup completed successfully!")
        print("\n🎙️ Starting voice recognition thread...")

        main.stop_listening = False
        main.stt_thread = threading.Thread(target=main.start_continuous_listening, daemon=True)
        main.stt_thread.start()

        print("✅ Voice recognition active!")

        return JSONResponse({
            "status": "success",
            "message": "Setup complete. Voice recognition active."
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))