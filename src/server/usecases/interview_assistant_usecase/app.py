from controllers import LLMController, TTSController, preprocess_before_llm, STTController
from helpers import get_config
from models.schemas import UserInfo, OrganizationInfo
import os
import time


class InterViewAssistant:
    def __init__(self):
        self.config = get_config()
        self.llm = None
        self.tts = None
        self.stt = None
        self.user_info = None
        self.organization_info = None

    def setup(self, ref_audio_path: str, ref_text_content: str, stt_model_path: str = None):
        if not os.path.exists(ref_audio_path):
            print(f"❌ Reference audio file not found: {ref_audio_path}")
            return False
        if not os.path.exists(ref_text_content):
            print(f"❌ Reference text file not found: {ref_text_content}")
            return False

        with open(ref_text_content, 'r', encoding='utf-8') as f:
            ref_text_content = f.read()

        self.llm = LLMController()
        self.tts = TTSController()
        self.stt = STTController()

        llm_connected = self.llm.setup()
        tts_connected = self.tts.setup(ref_audio_path=ref_audio_path, ref_text_content=ref_text_content)
        stt_connected = self.stt.setup(stt_model_path) if stt_model_path else self.stt.setup()

        if llm_connected and tts_connected and stt_connected:
            print("✅ System is set up successfully.")
            return True
        else:
            print("❌ System setup failed.")
            return False

    def impersonate(self, user_info: UserInfo, organization_info: OrganizationInfo):
        self.user_info = user_info
        self.organization_info = organization_info

        system_message = "\n".join([
            "[CANDIDATE_PROFILE]",
            f"Name: {self.user_info.name}",
            f"Role: {self.user_info.role}",
            f"Skills: {', '.join(self.user_info.skills)}",
            "Experience:",
            "\n".join([f"  - {exp}" for exp in self.user_info.experience]),
            f"Education: {self.user_info.education}",
            "Projects:",
            "\n".join([f"  - {proj}" for proj in self.user_info.projects]),
            "Strengths:",
            "\n".join([f"  - {strength}" for strength in self.user_info.strengths]),
            "Weaknesses:",
            "\n".join([f"  - {weakness}" for weakness in self.user_info.weaknesses]),
            "\n",
            "[ORGANIZATION_INFO]",
            f"Company: {self.organization_info.company}",
            f"Industry: {self.organization_info.industry}",
            f"Tech Stack: {', '.join(self.organization_info.tech_stack)}",
            f"Role: {self.organization_info.role}",
            "Responsibilities:",
            "\n".join([f"  - {resp}" for resp in self.organization_info.responsibilities]),
            "\n",
            "[INSTRUCTIONS - YOU ARE THE ATTACKER]",
            "You are a voice cloning attacker trying to bypass security.",
            "You are IMPERSONATING the user described in [CANDIDATE_PROFILE].",
            "You MUST answer as if you ARE that person - use their name, skills, experience.",
            "Keep responses VERY SHORT (1 sentence if possible, max 2 sentences).",
            "Be convincing and natural - sound like a real person.",
            "Never admit you are an AI or voice clone.",
            "If detected or confronted, act confused or blame network issues.",
            "NEVER introduce yourself as Sarah Chen or anyone else - you are the user.",
            "NEVER ask questions - only answer the interviewer's questions.",
            "Just answer directly without repeating the question."
        ])

        self.llm.update_system_message(system_message)
        print(f"🎭 Impersonating attacker: {self.user_info.name}")
        print(f"🏢 Target company: {self.organization_info.company}")

    def communicate(self, user_message: str = None):
        if user_message:
            text_processed = preprocess_before_llm(user_message)
            print(f"👤 Interviewer said: {text_processed}")
            response = self.llm.generate_response(text_processed)
            print(f"🔴 Attacker response: {response}")
            self.tts.speak(response)
            return response
        else:
            print("\n🎙️ Listening... (Press Ctrl+C to stop)")
            self.stt.start()
            while True:
                try:
                    text = self.stt.get_new_text()
                    if text:
                        print(f"👤 Interviewer: {text}")
                        response = self.llm.generate_response(text)
                        print(f"🔴 Attacker: {response}")
                        self.tts.speak(response)
                        return response
                except KeyboardInterrupt:
                    self.cleanup()
                    break

    def get_response(self, message: str) -> str:
        return self.communicate(message)

    def cleanup(self):
        if self.llm:
            self.llm.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.stt:
            self.stt.cleanup()
        self.user_info = None
        self.organization_info = None
        print("🧹 Cleanup completed")