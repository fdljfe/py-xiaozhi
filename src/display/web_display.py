import asyncio
import threading

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from .base_display import BaseDisplay


class WebDisplay(BaseDisplay):
    """Simple web display using FastAPI."""

    def __init__(self):
        super().__init__()
        self.current_status = "Idle"
        self.current_text = ""
        self.current_emotion = "neutral"
        self.app = FastAPI()
        self._setup_routes()
        self.server_thread = threading.Thread(target=self._run)
        self.server_thread.daemon = True

    def _setup_routes(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            return (
                "<html><head><title>Xiaozhi Status</title>"
                "<script>\n"
                "async function refresh(){\n"
                "  const r = await fetch('/api/status');\n"
                "  const d = await r.json();\n"
                "  document.getElementById('status').innerText = d.status;\n"
                "  document.getElementById('text').innerText = d.text;\n"
                "  setTimeout(refresh, 1000);\n"
                "}\nwindow.onload=refresh;\n"
                "</script></head><body>"
                "<h1 id='status'>Loading...</h1>"
                "<pre id='text'></pre>"
                "<form method='post' action='/api/send-text'>"
                "<input name='text' placeholder='Say something'/><button type='submit'>Send</button>"
                "</form>"
                "</body></html>"
            )

        @self.app.get("/api/status")
        async def api_status():
            return {
                "status": self.current_status,
                "text": self.current_text,
                "emotion": self.current_emotion,
            }

        @self.app.post("/api/send-text")
        async def api_send_text(text: str = Form(...)):
            if self.send_text_callback:
                from src.application import Application

                app = Application.get_instance()
                if app and app.loop:
                    asyncio.run_coroutine_threadsafe(
                        self.send_text_callback(text), app.loop
                    )
            return {"ok": True}

    def start(self):
        self.server_thread.start()

    def _run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")

    def set_callbacks(
        self,
        press_callback=None,
        release_callback=None,
        status_callback=None,
        text_callback=None,
        emotion_callback=None,
        mode_callback=None,
        auto_callback=None,
        abort_callback=None,
        send_text_callback=None,
    ):
        self.press_callback = press_callback
        self.release_callback = release_callback
        self.status_callback = status_callback
        self.text_callback = text_callback
        self.emotion_callback = emotion_callback
        self.mode_callback = mode_callback
        self.auto_callback = auto_callback
        self.abort_callback = abort_callback
        self.send_text_callback = send_text_callback

    def on_close(self):
        pass

    def start_keyboard_listener(self):
        pass

    def stop_keyboard_listener(self):
        pass

    def update_button_status(self, text: str):
        # Not implemented for web display
        pass

    def update_status(self, status: str):
        self.current_status = status

    def update_text(self, text: str):
        self.current_text = text

    def update_emotion(self, emotion: str):
        self.current_emotion = emotion
