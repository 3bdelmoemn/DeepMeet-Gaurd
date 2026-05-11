from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/api/chat")
async def chat(request: ChatRequest):
    from main import assistant
    
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