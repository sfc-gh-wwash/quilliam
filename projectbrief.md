# Meeting Notes AI Demo — Project Brief

## What This Is

A real-time meeting recorder and AI-powered note-taking application built on Snowflake. During a meeting, the app records audio, transcribes it live, and automatically extracts structured notes: attendees mentioned, decisions made, action items assigned, topics discussed, and key dates. At the end of the meeting, users get a clean, searchable summary stored entirely in Snowflake.

This demo repurposes the architecture from the Call Center AI demo — the same audio pipeline, Snowflake stage upload, and Cortex AI functions — but refocused on a meeting productivity use case that resonates with any knowledge worker audience.

---

## The Demo Scenario

> A team meets to discuss a product launch. The app records the conversation, and by the time the meeting ends, every action item is already logged, every decision is captured, and the notes are searchable alongside past meetings.

**Flow:**

1. **Meeting starts** → User clicks Record in the React app
2. **Audio captured** → PyAudio records microphone, chunked into 10-second MP3 segments
3. **Snowflake transcribes** → Each chunk uploaded to a Snowflake stage, `ai_transcribe()` converts to text
4. **AI extracts structure** → `ai_extract()` pulls out attendees, action items, decisions, topics, and dates
5. **Live notes panel updates** → WebSocket pushes results to the UI in real time as the meeting progresses
6. **Meeting ends** → Full summary generated from all extracted notes

---

## Core Snowflake AI Functions

| Function | Role in This Demo |
|---|---|
| `ai_transcribe()` | Converts staged MP3 audio chunks to text as the meeting progresses |
| `ai_extract()` | Pulls structured fields (attendees, actions, decisions, topics) from transcript text |

All AI runs inside Snowflake — no external APIs, no data movement.

---

## Extraction Fields (replaces call center's 9 fields)

`ai_extract()` will be configured to pull these fields from each transcript chunk:

- **attendees** — names of people mentioned or introduced
- **action_items** — tasks assigned, with owner and due date if mentioned
- **decisions** — conclusions or agreements reached
- **topics** — high-level themes or agenda items discussed
- **key_dates** — deadlines, milestones, or dates referenced
- **blockers** — risks or issues flagged by participants
- **follow_ups** — things to revisit or schedule later
- **meeting_title** — inferred name for the meeting if mentioned

---

## Data Model (replaces call center tables)

| Table | Type | Purpose |
|---|---|---|
| `MEETINGS` | Hybrid Table | One row per meeting session (id, title, started_at, ended_at, status) |
| `MEETING_TRANSCRIPTS` | Regular Table | Chunked transcript text with meeting_id, chunk number, timestamp |
| `MEETING_EXTRACTIONS` | Regular Table | Raw `ai_extract()` output per chunk (JSON) |
| `ACTION_ITEMS` | Hybrid Table | De-duplicated actions across chunks (owner, due_date, status) |
| `DECISIONS` | Regular Table | Captured decisions with meeting_id and transcript reference |

---

## Architecture

```
React Frontend (localhost:3000)
    ⇄ WebSocket (real-time updates)
    ⇄ FastAPI Backend (localhost:8080)
          ↓
    PyAudio → 10s MP3 chunks (triple-stream: primary, boundary-overlap, archive)
          ↓
    PUT → @MEETINGS.STG.AUDIO (Snowflake Internal Stage, SSE encrypted)
          ↓
    ai_transcribe() → MEETING_TRANSCRIPTS table
          ↓
    ai_extract() → MEETING_EXTRACTIONS → ACTION_ITEMS + DECISIONS
          ↓
    WebSocket push → React UI updates live notes panel
```

---

## UI Panels (replaces agent assist panels)

| Panel | Description |
|---|---|
| **Live Transcript** | Rolling view of the transcribed conversation as it comes in |
| **Action Items** | Real-time list of tasks extracted, with inferred owner and due date |
| **Decisions** | Bullet list of agreements/conclusions captured so far |
| **Key Topics** | Tag cloud or list of topics identified in the conversation |
| **Meeting Summary** | Generated at end of meeting: full structured recap |

---

## What Changes from the Call Center Demo

| Call Center | Meeting Notes |
|---|---|
| Customer calls about a defective product | Team discusses a project/topic |
| 9 extraction fields (name, phone, order #, etc.) | 8 extraction fields (attendees, actions, decisions, etc.) |
| Customer identification + order history lookup | No customer lookup; attendee names are extracted |
| Similar case detection (defect patterns) | ~~Removed~~ — no similarity matching |
| Agent assistance UI | Meeting notes/summary UI for the meeting host |
| `CUSTOMERS`, `ORDERS`, `CASES` tables | `MEETINGS`, `ACTION_ITEMS`, `DECISIONS` tables |
| Demo scenario: headphone defect | Demo scenario: product launch planning meeting |

The audio pipeline (PyAudio triple-stream, PUT to stage, `ai_transcribe()`) stays exactly the same. The WebSocket real-time push pattern stays exactly the same. Only the extraction schema, data model, and UI panels change.

---

## Demo Scenario Details

**Meeting:** "Q3 Product Launch Planning"
**Attendees:** Sarah (PM), Marcus (Eng), Priya (Marketing)

The sample meeting recording (or scripted live demo) covers:
- Confirming the September 15 launch date
- Marcus agreeing to finish the API by August 30
- Priya flagging a risk: "We still don't have sign-off from legal on the new pricing page"
- Decision: "We'll go with the beta feature set, not the full roadmap"

By the end, the UI shows:
- 3 action items with owners and dates automatically extracted
- 1 blocker (legal sign-off)
- 1 key decision captured

---

## Snowflake Features to Highlight

- `ai_transcribe()` — speech-to-text inside Snowflake, no external API
- `ai_extract()` — structured extraction from unstructured meeting conversation
- **Hybrid Tables** — low-latency reads for real-time UI updates on action items
- **Internal Stage** — audio file storage with SSE encryption required by AI functions
- **Cortex AI** — all intelligence runs as SQL, on your data, in your account

---

## Tech Stack

- **Frontend:** React (Vite), WebSocket client
- **Backend:** FastAPI (Python), WebSocket server
- **Audio:** PyAudio + pydub (MP3 encoding)
- **Database:** Snowflake (Python connector)
- **AI:** Snowflake Cortex (`ai_transcribe`, `ai_extract`)
