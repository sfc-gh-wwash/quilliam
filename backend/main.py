import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from typing import List

from snowflake_manager import SnowflakeManager
from audio_recorder import AudioRecorder
from api_routes import router, set_global_instances

load_dotenv(dotenv_path="../.env")

app = FastAPI(title="Meeting Notes Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

snowflake_manager = None
audio_recorder = None
active_websockets: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    global snowflake_manager, audio_recorder

    snowflake_manager = SnowflakeManager()
    await snowflake_manager.connect()

    audio_recorder = AudioRecorder(snowflake_manager)
    audio_recorder.set_update_callback(broadcast_to_websockets)
    set_global_instances(audio_recorder, snowflake_manager)

    print("Meeting Notes Backend started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    global snowflake_manager, audio_recorder

    if audio_recorder:
        await audio_recorder.stop_recording()
    if snowflake_manager:
        await snowflake_manager.disconnect()

    print("Meeting Notes Backend shut down")

@app.get("/")
async def root():
    return {"message": "Meeting Notes Demo API is running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "snowflake_connected": snowflake_manager.is_connected() if snowflake_manager else False,
        "audio_available": audio_recorder.is_available() if audio_recorder else False
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

async def broadcast_to_websockets(message: dict):
    if active_websockets:
        disconnected = []
        for websocket in active_websockets:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        for ws in disconnected:
            active_websockets.remove(ws)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
