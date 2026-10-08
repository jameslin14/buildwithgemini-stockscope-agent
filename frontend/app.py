"""Standalone Chat & A2UI Web App for StockScope AI using local ADK Runner."""
import asyncio
import json
import os
import uuid
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from dotenv import load_dotenv

# Ensure environment variables (.env) are loaded for Vertex AI / ADC
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-c7f7b6dbf6e7")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from app.agent import app as adk_app

app = FastAPI(title="StockScope AI")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

session_service = InMemorySessionService()
runner = Runner(
    app=adk_app,
    session_service=session_service,
    auto_create_session=True,
)

USER_SESSIONS: Dict[str, str] = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = os.path.join(static_dir, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat")
async def chat(request: Request):
    payload = await request.json()
    user_message = payload.get("message", "").strip()
    session_id = payload.get("session_id") or str(uuid.uuid4())
    user_id = payload.get("user_id", "default_user")

    if not user_message:
        return JSONResponse({"error": "Empty message"}, status_code=400)

    parts_out: List[Dict[str, Any]] = []

    user_content = Content(
        role="user",
        parts=[Part.from_text(text=user_message)],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Check for inline_data containing A2UI payload
                raw_data = None
                if hasattr(part, "inline_data") and part.inline_data:
                    raw_data = part.inline_data.data
                elif hasattr(part, "data") and part.data:
                    raw_data = part.data

                if raw_data:
                    try:
                        import base64
                        if isinstance(raw_data, bytes):
                            text_repr = raw_data.decode("utf-8")
                        else:
                            try:
                                text_repr = base64.b64decode(raw_data).decode("utf-8")
                            except Exception:
                                text_repr = str(raw_data)
                        if "<a2a_datapart_json>" in text_repr:
                            inner = text_repr.split("<a2a_datapart_json>")[1].split("</a2a_datapart_json>")[0]
                            parsed = json.loads(inner)
                            if "data" in parsed:
                                parts_out.append({"kind": "a2ui", "data": parsed["data"]})
                            else:
                                parts_out.append({"kind": "a2ui", "data": parsed})
                            continue
                    except Exception:
                        pass

                if hasattr(part, "text") and part.text:
                    parts_out.append({"kind": "text", "text": part.text})

    return JSONResponse({
        "session_id": session_id,
        "parts": parts_out,
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
