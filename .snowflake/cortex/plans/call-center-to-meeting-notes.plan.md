# Plan: Call Center → Meeting Notes Refactor

## Overview
Refactor the existing working Call Center AI demo into a Meeting Notes AI demo. The audio pipeline (PyAudio triple-stream → Snowflake stage → `ai_transcribe()`) is preserved unchanged. Everything else — Snowflake objects, extraction fields, backend logic, API routes, and frontend UI — is replaced.

## Snowflake Target
- **Database:** `MEETING_NOTES`, schema `STG`
- **Stage:** `@MEETING_NOTES.STG.AUDIO` (SSE encrypted, required for `ai_transcribe()`)
- **User/Role:** `MEETING_NOTES_ADMIN` / `MEETING_NOTES_ADMIN_RL`
- **Warehouse:** `MEETING_NOTES_WH`

---

## Task 1 — `database/meeting_notes_ddl.sql` (new file)

New tables replacing all call center tables:

| Table | Type | Key Columns |
|---|---|---|
| `MEETINGS` | Hybrid | id, title, started_at, ended_at, status |
| `MEETING_TRANSCRIPTS` | Regular | meeting_id, chunk_number, transcript_text, audio_duration |
| `MEETING_EXTRACTIONS` | Regular | meeting_id, chunk_number, raw_json (full ai_extract output) |
| `ACTION_ITEMS` | Hybrid | id, meeting_id, owner, task, due_date, status |
| `DECISIONS` | Regular | id, meeting_id, decision_text, chunk_number |

Also includes: CREATE USER, ROLE, WAREHOUSE, GRANTs.

---

## Task 2 — `.env`

```
SNOWFLAKE_USER=MEETING_NOTES_ADMIN
SNOWFLAKE_WAREHOUSE=MEETING_NOTES_WH
SNOWFLAKE_DATABASE=MEETING_NOTES
SNOWFLAKE_SCHEMA=STG
SNOWFLAKE_ROLE=MEETING_NOTES_ADMIN_RL
```
Account and private key path stay the same.

---

## Task 3 — `backend/snowflake_manager.py`

**Remove:**
- `get_customer_info`, `get_customer_orders`, `get_order_items`
- `lookup_order`, `lookup_customers_from_candidates`
- `get_similar_cases`, `match_product_from_order_history`, `match_products_from_candidates`
- `generate_case_number`, `generate_call_number`
- `select_candidate_value`, `get_candidate_values`

**Replace:**
- `upload_mp3_to_stage` — stage path changes to `@MEETING_NOTES.STG.AUDIO`
- `process_audio_transcription` — inserts into `MEETING_TRANSCRIPTS` with meeting_id, chunk_number
- `extract_candidate_values` → `extract_meeting_notes` — new `ai_extract()` schema with 8 fields (attendees, action_items, decisions, topics, key_dates, blockers, follow_ups, meeting_title); upserts into `ACTION_ITEMS` and `DECISIONS`

**Add:**
- `generate_meeting_id` — replaces generate_case/call_number
- `get_meeting_extractions(meeting_id)` — returns aggregated extractions for a meeting
- `get_meeting_transcript(meeting_id)` — returns ordered transcript chunks

**`ai_extract()` response format:**
```json
{
  "attendees": ["list of names"],
  "action_items": [{"owner": "name", "task": "description", "due_date": "date or null"}],
  "decisions": ["list of decisions"],
  "topics": ["list of topics"],
  "key_dates": ["list of dates/deadlines"],
  "blockers": ["list of risks/blockers"],
  "follow_ups": ["things to revisit"],
  "meeting_title": "inferred title"
}
```

---

## Task 4 — `backend/audio_recorder.py`

- Rename `current_claim_number` / `current_call_number` → `current_meeting_id`
- Update `start_recording(meeting_id)` signature
- Remove the three `try` blocks for customer lookup, similar cases, product matching
- Update WebSocket payload:
```json
{
  "type": "meeting_updated",
  "meeting_id": "...",
  "transcript_chunk": "...",
  "action_items": [...],
  "decisions": [...],
  "topics": [...],
  "attendees": [...],
  "blockers": [...]
}
```

---

## Task 5 — `backend/api_routes.py`

**Remove routes:**
- `/customer/search`, `/order/lookup`, `/case/generate`, `/call/generate`
- `/candidates/{case_id}`, `/candidates/{case_id}/{call_id}`
- `/candidates/{candidate_id}/select`
- `/customers/lookup/{case_id}/{call_id}`
- `/cases/similar/{case_id}/{call_id}`
- `/products/match/{customer_id}/{case_id}/{call_id}`

**Replace/Add routes:**
- `POST /meetings/start` — generates meeting_id, starts recording
- `POST /meetings/stop` — stops recording
- `GET /meetings/status` — is_recording, current_meeting_id
- `GET /meetings/{meeting_id}/extractions` — returns action_items, decisions, topics, attendees, blockers
- `GET /meetings/{meeting_id}/transcript` — returns ordered transcript text

---

## Task 6 — `backend/main.py`

- Change `FastAPI(title="Call Center Demo API")` → `"Meeting Notes Demo API"`
- Update print statements

---

## Task 7 — `frontend/src/AudioRecorder.js`

**Remove state/UI:**
- `caseNumber`, `callNumber`, `phoneNumber` state
- `candidateValues`, `showCandidates`, `expandedTranscripts`
- `customerSearch`, `customerInfo`, `matchedCustomers`
- `orderSearch`, `orderInfo`
- `similarCases`, `matchedProducts`, `showSimilarCases`, `showProductMatch`
- Customer Lookup section, Order lookup section
- Similar Cases panel, Product Match panel
- Call Details form (all the form fields)
- "Call Simulator" section header + phone input

**Add state/UI:**
- `meetingId` — current meeting session ID
- `transcriptChunks` — array of transcript text chunks (live rolling view)
- `actionItems` — array of `{owner, task, due_date}`
- `decisions` — array of strings
- `topics` — array of strings
- `attendees` — array of strings
- `blockers` — array of strings

**New panels:**
1. **Meeting Recorder** — device selector, Start/Stop button, meeting ID display
2. **Live Transcript** — rolling display of transcript chunks as they arrive
3. **Action Items** — table of owner/task/due_date
4. **Decisions** — bulleted list
5. **Key Topics & Attendees** — two-column tag display
6. **Blockers** — warning-style list

WebSocket handler: listens for `meeting_updated` messages, merges new data into state arrays.

---

## Task 8 — `frontend/src/App.js`

- Change hero title to: `Meeting Notes AI  Powered by Snowflake`
- Change subtitle to: `Real-time transcription · AI extraction · Structured meeting notes`
