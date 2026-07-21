# Quilliam

Real-time meeting recorder and AI-powered note-taker built on Snowflake. Records audio, transcribes it live with `ai_transcribe()`, and extracts structured meeting notes using `ai_extract()` — all running inside Snowflake with no external AI services.

## What It Does

1. Click **Start Meeting** — audio recording begins
2. Every 10 seconds, a chunk is uploaded to a Snowflake stage and transcribed
3. `ai_extract()` pulls out attendees, action items, decisions, topics, blockers, and key dates
4. The UI updates live via WebSocket as each chunk is processed
5. Click **End Meeting** — final decisions are extracted and the meeting is saved
6. Browse past meetings in the sidebar, edit notes, add/remove action items and decisions

## Architecture

```
React Frontend (localhost:3000)
    ⇄ WebSocket (real-time updates)
    ⇄ FastAPI Backend (localhost:8080)
          ↓
    PyAudio → 10s MP3 chunks (triple-stream recording)
          ↓
    PUT → @QUILLIAM.STG.AUDIO (Snowflake internal stage, SSE encrypted)
          ↓
    ai_transcribe() → MEETING_TRANSCRIPTS
          ↓
    ai_extract() → ACTION_ITEMS + DECISIONS + MEETING_EXTRACTIONS
          ↓
    WebSocket push → React UI live panels
```

## Snowflake AI Functions Used

| Function | Role |
|---|---|
| `ai_transcribe()` | Converts staged MP3 audio to text inside Snowflake |
| `ai_extract()` | Extracts structured fields from transcript text |

## Tech Stack

- **Frontend:** React (Create React App), WebSocket
- **Backend:** FastAPI, PyAudio, pydub
- **Database:** Snowflake (QUILLIAM database, Hybrid Tables for low-latency reads)
- **AI:** Snowflake Cortex (`ai_transcribe`, `ai_extract`)

## Setup

### Prerequisites

- Python 3.11+
- Node 18+
- PortAudio (`brew install portaudio` on macOS)
- Snowflake account with Cortex AI enabled

### 1. Run the DDL

Execute `database/meeting_notes_ddl.sql` in your Snowflake account as ACCOUNTADMIN. This creates the database, schema, stage, tables, user, role, and warehouse.

### 2. Configure key-pair auth

Generate an RSA key pair and place the private key at `backend/rsa_key.p8`:

```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out backend/rsa_key.p8 -nocrypt
openssl rsa -in backend/rsa_key.p8 -pubout -out backend/rsa_key.pub
```

Set the public key on the Snowflake user:

```sql
ALTER USER QUILLIAM_ADMIN SET RSA_PUBLIC_KEY='<contents of rsa_key.pub without headers>';
```

### 3. Configure .env

Copy `.env.example` or create `.env` in the project root:

```
SNOWFLAKE_ACCOUNT=<your-account>
SNOWFLAKE_USER=QUILLIAM_ADMIN
SNOWFLAKE_PRIVATE_KEY_PATH=./rsa_key.p8
SNOWFLAKE_WAREHOUSE=QUILLIAM_WH
SNOWFLAKE_DATABASE=QUILLIAM
SNOWFLAKE_SCHEMA=STG
SNOWFLAKE_ROLE=QUILLIAM_ADMIN_RL
PORT=8080
```

### 4. Start the app

```bash
./start.sh
```

This installs dependencies, starts the backend on port 8080, and the frontend on port 3000.

### 5. Use it

Open http://localhost:3000, select a microphone, and click **Start Meeting**.

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app, WebSocket server
│   ├── api_routes.py        # REST endpoints
│   ├── audio_recorder.py    # PyAudio triple-stream recording
│   ├── snowflake_manager.py # Snowflake connection, AI function calls, CRUD
│   └── requirements.txt
├── frontend/src/
│   ├── App.js               # Layout: header + sidebar + main
│   ├── Sidebar.js           # Meeting list
│   ├── AudioRecorder.js     # Live recording + real-time panels
│   └── MeetingDetail.js     # Past meeting view with edit
├── database/
│   └── meeting_notes_ddl.sql # Full Snowflake setup
├── start.sh / stop.sh / restart.sh
└── .env                     # (not committed)
```
