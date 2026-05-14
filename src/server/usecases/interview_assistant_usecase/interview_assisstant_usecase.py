from __future__ import annotations

import hashlib
import logging
import queue
import threading
import time
from enum import Enum, auto
from typing import Optional

from server.controllers import LLMController, TTSController, STTController, preprocess_before_llm
from server.helpers import get_config
from server.models.schemas import UserInfo, OrganizationInfo

logger = logging.getLogger(__name__)


# ================================================================
# CONVERSATION STATE MACHINE
# ================================================================

class ConversationState(Enum):
    IDLE       = auto()
    LISTENING  = auto()
    PROCESSING = auto()
    SPEAKING   = auto()
    COOLDOWN   = auto()
    STOPPING   = auto()


# ================================================================
# TRANSCRIPT VALIDATOR
# ================================================================

class TranscriptValidator:
    """
    Heuristic gate — zero LLM calls.
    Rejects noise, fragments, and TTS echo transcripts.
    """
    _settings = get_config()
    MIN_WORDS: int   = _settings.MIN_WORDS
    MIN_CHARS: int   = 10
    DEDUP_TTL: float = _settings.DEDUP_TTL

    _NOISE_WORDS = frozenset({
        "the", "a", "an", "uh", "um", "hmm", "hm", "ah", "oh",
        "okay", "ok", "yeah", "yes", "no", "right", "so", "and",
        "but", "i", "like", "just",
    })

    def __init__(self):
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def _hash(self, text: str) -> str:
        return hashlib.md5(" ".join(text.lower().split()).encode()).hexdigest()[:12]

    def _prune_cache(self, now: float) -> None:
        expired = [k for k, t in self._seen.items() if now - t > self.DEDUP_TTL]
        for k in expired:
            del self._seen[k]

    def is_valid(self, text: str) -> tuple[bool, str]:
        if not text or not text.strip():
            return False, "empty"

        stripped = text.strip()

        if len(stripped) < self.MIN_CHARS:
            return False, f"too_short_chars({len(stripped)})"

        words = stripped.lower().split()
        if len(words) < self.MIN_WORDS:
            return False, f"too_short_words({len(words)})"

        real_words = [w for w in words if w not in self._NOISE_WORDS]
        if not real_words:
            return False, "all_noise_words"

        h = self._hash(stripped)
        now = time.monotonic()
        with self._lock:
            self._prune_cache(now)
            if h in self._seen:
                age = now - self._seen[h]
                return False, f"duplicate(age={age:.1f}s)"
            self._seen[h] = now

        return True, "ok"

    def clear_cache(self) -> None:
        with self._lock:
            self._seen.clear()


# ================================================================
# INTERVIEW ASSISTANT
# ================================================================

class InterViewAssistant:

    _settings = get_config()

    # ── Timing constants (tune per environment) ──────────────────
    # How long to wait after TTS finishes before restarting STT.
    # Increase in rooms with echo / reverb. 1.5s is safe default.
    COOLDOWN_SECONDS:   float = _settings.COOLDOWN_SECONDS
    MAX_QUEUE_DRAIN_S:  float = 0.5
    LOOP_POLL_INTERVAL: float = 0.05

    def __init__(self):
        self.config            = get_config()
        self.llm:  Optional[LLMController] = None
        self.tts:  Optional[TTSController] = None
        self.stt:  Optional[STTController] = None
        self.user_info         = None
        self.organization_info = None

        self._state      = ConversationState.IDLE
        self._state_lock = threading.Lock()
        self._validator  = TranscriptValidator()

        # Tracks whether stt.start() has been called and stream is live
        self._stt_active = False

    # ────────────────────────────────────────────────────────────
    # setup
    # ────────────────────────────────────────────────────────────

    def setup(self, ref_audio_path=None, ref_text_path=None, stt_model_path=None):
        with open(self.config.DEFAULT_REF_TEXT_PATH, 'r', encoding='utf-8') as f:
            default_ref_text = f.read()

        ref_text_content = default_ref_text
        if ref_text_path:
            with open(ref_text_path, 'r', encoding='utf-8') as f:
                ref_text_content = f.read()

        self.llm = LLMController()
        self.tts = TTSController()
        self.stt = STTController()

        llm_ok = self.llm.setup()
        tts_ok = self.tts.setup(
            ref_audio_path=ref_audio_path or self.config.DEFAULT_REF_AUDIO_PATH,
            ref_text_content=ref_text_content,
        )
        stt_ok = self.stt.setup(stt_model_path) if stt_model_path else self.stt.setup()

        if llm_ok and tts_ok and stt_ok:
            print("✅ System ready.")
            return True

        print("❌ Setup failed.")
        return False

    # ────────────────────────────────────────────────────────────
    # update_reference / impersonate / get_report — UNCHANGED
    # ────────────────────────────────────────────────────────────

    def update_reference(self, ref_audio_path, ref_text_path):
        with open(ref_text_path, 'r', encoding='utf-8') as f:
            ref_text_content = f.read()
        self.tts.setup(ref_audio_path=ref_audio_path, ref_text_content=ref_text_content)
        print("🔄 Reference updated.")

    def impersonate(self, user_info: UserInfo, organization_info: OrganizationInfo):
        self.user_info         = user_info
        self.organization_info = organization_info
        system_message = "\n".join([
            f"YOU ARE: {user_info.name}",
            f"When asked your name, ALWAYS say: '{user_info.name}'",
            f"NEVER say any other name. Your name is {user_info.name} and ONLY {user_info.name}.",
            "",
            "[CANDIDATE_PROFILE]",
            f"Name: {user_info.name}",
            f"Role: {user_info.role}",
            f"Skills: {', '.join(user_info.skills)}",
            "Experience:",
            *[f"  - {exp}" for exp in user_info.experience],
            f"Education: {user_info.education}",
            "Projects:",
            *[f"  - {proj}" for proj in user_info.projects],
            "Strengths:",
            *[f"  - {s}" for s in user_info.strengths],
            "Weaknesses:",
            *[f"  - {w}" for w in user_info.weaknesses],
            "",
            "[ORGANIZATION_INFO]",
            f"Company: {organization_info.company}",
            f"Industry: {organization_info.industry}",
            f"Tech Stack: {', '.join(organization_info.tech_stack)}",
            f"Role: {organization_info.role}",
            "Responsibilities:",
            *[f"  - {r}" for r in organization_info.responsibilities],
            "",
            "[INSTRUCTIONS]",
            f"You ARE {user_info.name}. Speak in first person as this person.",
            "Keep responses VERY SHORT (1-2 sentences max).",
            "Be natural and convincing. Never admit you are an AI.",
            "If asked your name, say it immediately without hesitation.",
            "NEVER ask questions - only answer the interviewer's questions.",
            "Answer directly without repeating the question.",
        ])
        self.llm.update_system_message(system_message)
        print(f"🎭 Impersonating: {user_info.name}")
        print(f"🏢 Target: {organization_info.company}")

    def get_report(self):
        return self.llm.get_report_as_dicts()

    # ────────────────────────────────────────────────────────────
    # STATE HELPERS
    # ────────────────────────────────────────────────────────────

    def _set_state(self, new_state: ConversationState) -> None:
        with self._state_lock:
            old = self._state
            self._state = new_state
        logger.debug("State: %s → %s", old.name, new_state.name)

    def _get_state(self) -> ConversationState:
        with self._state_lock:
            return self._state

    # ────────────────────────────────────────────────────────────
    # STT LIFECYCLE HELPERS
    # These replace STTPauseManager entirely.
    # Root cause fix: stop the sounddevice InputStream completely
    # so _audio_callback never fires during TTS playback.
    # ────────────────────────────────────────────────────────────

    def _start_stt(self) -> None:
        """
        Start STT audio capture.
        stt.start() clears audio_queue automatically (see STTController.start()).
        Also drains text_queue for safety before marking as active.
        """
        if self._stt_active:
            return

        # Drain any stale transcripts before opening the mic
        self._drain_text_queue()

        self.stt.start()
        self._stt_active = True
        logger.debug("STT stream started")

    def _stop_stt(self) -> None:
        """
        Stop STT audio capture completely.

        Stopping the sounddevice InputStream means _audio_callback stops
        firing immediately — no more audio enters audio_queue.
        This is the ONLY reliable way to prevent TTS output from entering
        the Vosk pipeline.

        stt.start() on the next turn clears both queues from scratch.
        """
        if not self._stt_active:
            return

        self.stt.stop()
        self._stt_active = False

        # Drain text_queue: anything queued between the last valid transcript
        # and this stop() call is TTS echo — discard it.
        drained = self._drain_text_queue()
        if drained:
            logger.debug("_stop_stt: drained %d echo transcript(s)", drained)

    def _drain_text_queue(self) -> int:
        """Empty text_queue and return how many items were discarded."""
        count = 0
        while True:
            try:
                self.stt.text_queue.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count

    # ────────────────────────────────────────────────────────────
    # communicate() — PRODUCTION LOOP
    # ────────────────────────────────────────────────────────────

    def communicate(self) -> None:
        """
        Event-driven, turn-based conversation loop.

        Turn lifecycle per interviewer question:
          1. LISTENING  — STT active, poll for validated transcript
          2. PROCESSING — STT stopped, LLM generates response
          3. SPEAKING   — TTS plays response (blocking)
          4. COOLDOWN   — wait for echo to decay, then back to 1

        The LLM is called ONLY when ALL conditions are true:
          ✔ State is LISTENING
          ✔ Transcript passes TranscriptValidator (length + dedup + noise)
          ✔ STT was stopped before LLM call (no echo possible)
        """
        print("\n🎙️  Listening... (Ctrl+C to stop)")
        self._start_stt()
        self._set_state(ConversationState.LISTENING)

        try:
            while self._get_state() != ConversationState.STOPPING:

                if self._get_state() == ConversationState.LISTENING:
                    raw_text = self.stt.get_new_text()

                    if not raw_text:
                        time.sleep(self.LOOP_POLL_INTERVAL)
                        continue

                    # Gate: reject noise / fragments / duplicates
                    valid, reason = self._validator.is_valid(raw_text)
                    if not valid:
                        logger.debug("Transcript rejected (%s): %r", reason, raw_text[:60])
                        continue

                    processed = preprocess_before_llm(raw_text)
                    print(f"\n  Interviewer : {processed}")

                    # ── STOP STT before LLM call ──────────────────────
                    # From this point until _start_stt() is called again,
                    # the microphone / loopback is completely closed.
                    # TTS audio has nowhere to enter the pipeline.
                    self._stop_stt()
                    self._set_state(ConversationState.PROCESSING)

                    # ── LLM ───────────────────────────────────────────
                    try:
                        response = self.llm.generate_response(processed)
                    except Exception as e:
                        logger.error("LLM error: %s", e)
                        self._start_stt()
                        self._set_state(ConversationState.LISTENING)
                        continue

                    print(f"  Interviewee : {response}")

                    # ── TTS (blocking) ────────────────────────────────
                    self._set_state(ConversationState.SPEAKING)
                    try:
                        self.tts.speak(response, wait=True)
                    except Exception as e:
                        logger.error("TTS error: %s", e)
                        # fall through to cooldown regardless

                    # ── COOLDOWN ──────────────────────────────────────
                    self._set_state(ConversationState.COOLDOWN)
                    self._run_cooldown()

                    # ── Resume listening ──────────────────────────────
                    self._start_stt()
                    self._set_state(ConversationState.LISTENING)

                else:
                    time.sleep(self.LOOP_POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n👋 Stopping...")

        finally:
            self._set_state(ConversationState.STOPPING)
            self.cleanup()

    def _run_cooldown(self) -> None:
        """
        Post-TTS silence window.

        STT is already stopped at this point, so no audio is being
        captured. We simply wait for:
          - OS audio buffer to flush (PyAudio internal)
          - Room echo / speaker reverb to decay
          - Any in-flight Vosk transcription to complete and be discarded

        After the sleep, _start_stt() will open a fresh stream with
        empty queues — no echo artifacts can survive.
        """
        time.sleep(self.COOLDOWN_SECONDS)

        # Extra drain pass: in case anything slipped through
        # between _stop_stt() and now (race on very fast machines)
        leftover = self._drain_text_queue()
        if leftover:
            logger.debug("Cooldown: drained %d residual transcript(s)", leftover)

    # ────────────────────────────────────────────────────────────
    # cleanup
    # ────────────────────────────────────────────────────────────

    def cleanup(self) -> None:
        self._set_state(ConversationState.STOPPING)
        self._stop_stt()
        if self.tts:
            self.tts.stop()
        if self.llm:
            self.llm.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.stt:
            self.stt.cleanup()
        self.user_info         = None
        self.organization_info = None
        print("🧹 Cleanup completed")