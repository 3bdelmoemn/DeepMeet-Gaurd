import os
import uuid
import json
import logging
from server.models.schemas import InterviewSetupRequest,UserInfo,OrganizationInfo
from server.helpers import get_config

settings = get_config()
logger = logging.getLogger(__name__)


def _normalize_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def _generate_user_id() -> str:
    return str(uuid.uuid4())


def _get_user_dir(user_id: str) -> str:
    return os.path.join(settings.SIMULATOR_STORAGE_PATH, user_id)


def _make_directory(path: str):
    os.makedirs(path, exist_ok=True)


# ============================================================
# Public Functions
# ============================================================

def create_user_session(interview_setup: InterviewSetupRequest) -> str:
    """
    Creates a folder for the user and saves their info.
    Returns the user_id (used in subsequent requests).
    """
    user_id = _generate_user_id()
    user_dir = _get_user_dir(user_id)
    _make_directory(user_dir)

    try:
        # Save user info
        user_info_path = os.path.join(user_dir, "user_info.json")
        with open(user_info_path, "w") as f:
            f.write(interview_setup.user_info.model_dump_json(indent=4))

        # Save organization info
        org_info_path = os.path.join(user_dir, "organization_info.json")
        with open(org_info_path, "w") as f:
            f.write(interview_setup.organization_info.model_dump_json(indent=4))

        # Save metadata
        meta = {
            "user_id": user_id,
            "name": interview_setup.user_info.name,
            "normalized_name": _normalize_name(interview_setup.user_info.name),
        }
        with open(os.path.join(user_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=4)

        logger.info(f"✅ User session created: {user_id}")

    except OSError as e:
        logger.error(f"❌ Failed to create session for {interview_setup.user_info.name}: {e}")
        raise

    return user_id


def get_user_audio_path(user_id: str, ext: str = ".wav") -> str:
    """Returns the path where the user's audio file should be saved."""
    user_dir = _get_user_dir(user_id)
    if not os.path.exists(user_dir):
        raise FileNotFoundError(f"User session not found: {user_id}")
    return os.path.join(user_dir, f"audio{ext}")


def get_user_text_path(user_id: str) -> str:
    """Returns the path where the user's reference text should be saved."""
    user_dir = _get_user_dir(user_id)
    if not os.path.exists(user_dir):
        raise FileNotFoundError(f"User session not found: {user_id}")
    return os.path.join(user_dir, "reference_text.txt")


def get_user_dir(user_id: str) -> str:
    """Returns the user's directory path."""
    user_dir = _get_user_dir(user_id)
    if not os.path.exists(user_dir):
        raise FileNotFoundError(f"User session not found: {user_id}")
    return user_dir

def get_user_session(user_id: str) -> tuple[UserInfo, OrganizationInfo]:
    """Loads user session data from disk."""
    user_dir = _get_user_dir(user_id)
    if not os.path.exists(user_dir):
        raise FileNotFoundError(f"User session not found: {user_id}")

    with open(os.path.join(user_dir, "user_info.json"), "r") as f:
        user_info = UserInfo(**json.load(f))

    with open(os.path.join(user_dir, "organization_info.json"), "r") as f:
        org_info = OrganizationInfo(**json.load(f))

    return user_info, org_info