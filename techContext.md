# Tech Context

## Technologies

### Frontend
- **React** (Vite) — SPA, no framework router needed
- **WebSocket API** (native browser) — real-time updates from backend
- **Fetch API** — REST calls for start/stop/history

### Backend
- **FastAPI** (Python) — REST endpoints + WebSocket server
- **PyAudio** — microphone capture
- **pydub** — MP3 encoding of raw PCM chunks
- **snowflake-connector-python** — Snowflake connection, PUT uploads, SQL execution
- **asyncio / threading** — concurrent audio streams + WebSocket management

### Snowflake
- **Internal Stage** with SSE encryption — audio file storage
- **ai_transcribe()** — speech-to-text Cortex function
- **ai_extract()** — structured extraction Cortex function
- **Hybrid Tables** — `MEETINGS` and `ACTION_ITEMS` for low-latency real-time reads
- **Regular Tables** — `MEETING_TRANSCRIPTS`, `MEETING_EXTRACTIONS`, `DECISIONS`

## Audio Capture Details
- Sample rate: 44,100 Hz
- Channels: 1 (mono)
- Chunk size: 10 seconds (primary stream)
- Overlap offset: 7 seconds (boundary stream)
- Format: MP3 (via pydub)

## Development Setup
- Python 3.11+
- Node 18+
- `pip install fastapi uvicorn pyaudio pydub snowflake-connector-python`
- `npm create vite@latest frontend -- --template react`
- PortAudio system dependency required for PyAudio (macOS: `brew install portaudio`)

## Snowflake Requirements
- Cortex AI functions enabled on the account
- `ai_transcribe()` requires internal stage with SSE encryption (not client-side encryption)
- Snowflake Python connector version >= 3.0 for modern PUT behavior
- Sufficient Cortex credits for transcription + extraction per demo run

## Environment Variables (backend)
```
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=  (or key-pair auth)
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
```

## Known Constraints
- `ai_transcribe()` is not streaming — it processes a complete file, so minimum latency is one full chunk (10s) plus processing time
- `ai_extract()` runs on the full aggregated transcript per chunk — gets more accurate as the meeting progresses
- PyAudio requires PortAudio on macOS; may need Homebrew setup on demo machine
