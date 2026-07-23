from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio

from audio_recorder import AudioRecorder
from snowflake_manager import SnowflakeManager

router = APIRouter(prefix="/api")

audio_recorder: Optional[AudioRecorder] = None
snowflake_manager: Optional[SnowflakeManager] = None


def set_global_instances(recorder: AudioRecorder, sf_manager: SnowflakeManager):
    global audio_recorder, snowflake_manager
    audio_recorder = recorder
    snowflake_manager = sf_manager


class DeviceInfo(BaseModel):
    index: int
    name: str
    max_input_channels: int
    default_sample_rate: float


class StartMeetingRequest(BaseModel):
    device_index: Optional[int] = None
    meeting_id: Optional[str] = None


class UpdateMeetingRequest(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None


class ActionItemRequest(BaseModel):
    owner: Optional[str] = None
    task: str
    due_date: Optional[str] = None
    status: Optional[str] = None


class DecisionRequest(BaseModel):
    text: str


class AgentChatRequest(BaseModel):
    message: str
    meeting_id: Optional[str] = None


# ------------------------------------------------------------------
# Audio devices
# ------------------------------------------------------------------

@router.get("/audio/devices")
async def get_audio_devices():
    if not audio_recorder:
        raise HTTPException(status_code=500, detail="Audio recorder not initialized")
    try:
        devices = audio_recorder.get_input_devices()
        return [DeviceInfo(**device) for device in devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audio devices: {str(e)}")


# ------------------------------------------------------------------
# Meeting recording lifecycle
# ------------------------------------------------------------------

@router.post("/meetings/start")
async def start_meeting(request: StartMeetingRequest):
    if not audio_recorder or not snowflake_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    try:
        meeting_id = request.meeting_id or await snowflake_manager.generate_meeting_id()

        await snowflake_manager.create_meeting(meeting_id)

        result = await audio_recorder.start_recording(
            meeting_id=meeting_id,
            device_index=request.device_index
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Auto-detect meeting title from calendar (fire-and-forget)
        asyncio.ensure_future(snowflake_manager.detect_meeting_title(meeting_id))

        return {
            "success": True,
            "message": "Meeting recording started",
            "meeting_id": meeting_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start meeting: {str(e)}")


@router.post("/meetings/stop")
async def stop_meeting():
    if not audio_recorder or not snowflake_manager:
        raise HTTPException(status_code=500, detail="Services not initialized")
    try:
        meeting_id = audio_recorder.current_meeting_id
        await audio_recorder.stop_recording()

        if meeting_id:
            await snowflake_manager.close_meeting(meeting_id)

        return {"success": True, "message": "Meeting recording stopped", "meeting_id": meeting_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop meeting: {str(e)}")


@router.get("/meetings/status")
async def get_meeting_status():
    if not audio_recorder:
        raise HTTPException(status_code=500, detail="Audio recorder not initialized")
    return {
        "is_recording": audio_recorder.is_recording,
        "current_meeting_id": audio_recorder.current_meeting_id
    }


# ------------------------------------------------------------------
# Meeting data
# ------------------------------------------------------------------

@router.get("/meetings/{meeting_id}/extractions")
async def get_meeting_extractions(meeting_id: str):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        data = await snowflake_manager.get_meeting_extractions(meeting_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get extractions: {str(e)}")


@router.get("/meetings/{meeting_id}/transcript")
async def get_meeting_transcript(meeting_id: str):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        chunks = await snowflake_manager.get_meeting_transcript(meeting_id)
        return {"meeting_id": meeting_id, "chunks": chunks, "count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {str(e)}")


# ------------------------------------------------------------------
# Meeting list & update
# ------------------------------------------------------------------

@router.get("/meetings")
async def list_meetings():
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        meetings = await snowflake_manager.list_meetings()
        return {"meetings": meetings, "count": len(meetings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list meetings: {str(e)}")


@router.put("/meetings/{meeting_id}")
async def update_meeting(meeting_id: str, request: UpdateMeetingRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.update_meeting(
            meeting_id, title=request.title, notes=request.notes,
            started_at=request.started_at, ended_at=request.ended_at
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update meeting")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update meeting: {str(e)}")


@router.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.delete_meeting(meeting_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete meeting")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")


@router.get("/meetings/deleted")
async def list_deleted_meetings():
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        all_meetings = await snowflake_manager.list_meetings(include_deleted=True)
        deleted = [m for m in all_meetings if m['status'] == 'DELETED']
        return {"meetings": deleted, "count": len(deleted)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list deleted meetings: {str(e)}")


@router.post("/meetings/{meeting_id}/restore")
async def restore_meeting(meeting_id: str):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.restore_meeting(meeting_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to restore meeting")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore meeting: {str(e)}")


# ------------------------------------------------------------------
# Action Items CRUD
# ------------------------------------------------------------------

@router.post("/meetings/{meeting_id}/action-items")
async def add_action_item(meeting_id: str, request: ActionItemRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        new_id = await snowflake_manager.add_action_item(meeting_id, request.owner, request.task, request.due_date)
        if new_id is None:
            raise HTTPException(status_code=400, detail="Failed to add action item")
        return {"success": True, "id": new_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add action item: {str(e)}")


@router.put("/action-items/{item_id}")
async def update_action_item(item_id: int, request: ActionItemRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.update_action_item(
            item_id, owner=request.owner, task=request.task, due_date=request.due_date, status=request.status
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update action item")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update action item: {str(e)}")


@router.delete("/action-items/{item_id}")
async def delete_action_item(item_id: int):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.delete_action_item(item_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete action item")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete action item: {str(e)}")


# ------------------------------------------------------------------
# Decisions CRUD
# ------------------------------------------------------------------

@router.post("/meetings/{meeting_id}/decisions")
async def add_decision(meeting_id: str, request: DecisionRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        new_id = await snowflake_manager.add_decision(meeting_id, request.text)
        if new_id is None:
            raise HTTPException(status_code=400, detail="Failed to add decision")
        return {"success": True, "id": new_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add decision: {str(e)}")


@router.put("/decisions/{decision_id}")
async def update_decision(decision_id: int, request: DecisionRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.update_decision(decision_id, request.text)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update decision")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update decision: {str(e)}")


@router.delete("/decisions/{decision_id}")
async def delete_decision(decision_id: int):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.delete_decision(decision_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete decision")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete decision: {str(e)}")


# ------------------------------------------------------------------
# Agent Chat
# ------------------------------------------------------------------

@router.post("/agent/chat")
async def agent_chat(request: AgentChatRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        response_text = await snowflake_manager.run_agent(request.message, request.meeting_id)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent chat failed: {str(e)}")


# ------------------------------------------------------------------
# MCP OAuth Connectors
# ------------------------------------------------------------------

class McpConnectRequest(BaseModel):
    integration: str = 'NOVA_MCP_INTEGRATION'

class McpCallbackRequest(BaseModel):
    query_string: str


@router.get("/mcp/connectors")
async def list_mcp_connectors():
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        connectors = await snowflake_manager.get_mcp_connectors()
        return {"connectors": connectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list MCP connectors: {str(e)}")


@router.post("/mcp/connect")
async def start_mcp_connect(request: McpConnectRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        auth_url = await snowflake_manager.start_mcp_oauth(request.integration)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start OAuth flow: {str(e)}")


@router.post("/mcp/callback")
async def finish_mcp_connect(request: McpCallbackRequest):
    if not snowflake_manager:
        raise HTTPException(status_code=500, detail="Snowflake manager not initialized")
    try:
        success = await snowflake_manager.finish_mcp_oauth(request.query_string)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete OAuth flow: {str(e)}")
