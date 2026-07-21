# System Patterns

## Architecture Overview

```
React Frontend (localhost:3000)
    ⇄ WebSocket — real-time push after each chunk is processed
    ⇄ HTTP REST — start/stop recording, fetch meeting history
    ⇄ FastAPI Backend (localhost:8080)
          ↓
    PyAudio → 10s MP3 chunks (triple-stream)
          ↓
    PUT → @MEETINGS.STG.AUDIO (Snowflake Internal Stage, SSE encrypted)
          ↓
    SELECT ai_transcribe(to_file(@stage, filename)) → INSERT MEETING_TRANSCRIPTS
          ↓
    SELECT ai_extract(aggregated_transcript, responseformat) → INSERT MEETING_EXTRACTIONS
          ↓
    Upsert de-duplicated ACTION_ITEMS, DECISIONS
          ↓
    WebSocket push → React UI updates live notes panel
```

## Audio Pipeline Pattern (Triple-Stream)

Inherited from the call center demo. Three concurrent PyAudio threads:
1. **Primary stream** — 10-second MP3 segments, processed immediately
2. **Overlap stream** — offset by 7 seconds, catches words that straddle segment boundaries
3. **Archive stream** — continuous full recording, written at end of meeting

The overlap stream prevents words at chunk boundaries from being dropped. The transcription pipeline de-duplicates overlapping text using chunk numbering.

## Snowflake Stage Upload Pattern

```python
conn.cursor().execute(f"PUT file://{local_path} @MEETINGS.STG.AUDIO auto_compress=false")
```

- Files named: `{meeting_id}_{chunk_number}_{timestamp}.mp3`
- Stage must use SSE encryption (required by `ai_transcribe()`)
- Files are cleaned up from stage after successful transcription (optional)

## Transcription Pattern

```sql
INSERT INTO MEETING_TRANSCRIPTS (meeting_id, chunk_number, transcript_text, audio_duration, created_at)
SELECT
    parse_filename_meeting_id(metadata$filename),
    parse_filename_chunk(metadata$filename),
    t.value:transcript::STRING,
    t.value:duration::FLOAT,
    CURRENT_TIMESTAMP()
FROM @MEETINGS.STG.AUDIO,
     LATERAL FLATTEN(input => ai_transcribe(to_file(@MEETINGS.STG.AUDIO, metadata$filename))) t
WHERE metadata$filename = :filename;
```

## Extraction Pattern

All transcript chunks for the current meeting are aggregated before extraction:

```sql
SELECT ai_extract(
    text => (SELECT LISTAGG(transcript_text, ' ') WITHIN GROUP (ORDER BY chunk_number)
             FROM MEETING_TRANSCRIPTS WHERE meeting_id = :meeting_id),
    responseformat => {
        "attendees": ["string"],
        "action_items": [{"owner": "string", "task": "string", "due_date": "string"}],
        "decisions": ["string"],
        "topics": ["string"],
        "key_dates": ["string"],
        "blockers": ["string"],
        "follow_ups": ["string"],
        "meeting_title": "string"
    }
)
```

## WebSocket Push Pattern

After each chunk is fully processed (transcribed + extracted), the backend sends a single JSON message:
```json
{
  "type": "update",
  "meeting_id": "...",
  "transcript_chunk": "...",
  "extractions": {
    "action_items": [...],
    "decisions": [...],
    "topics": [...],
    "attendees": [...],
    "blockers": [...]
  }
}
```

The frontend merges each update into its running state (union of all extraction results so far).

## Data Model

| Table | Type | Key Columns |
|---|---|---|
| `MEETINGS` | Hybrid Table | id, title, started_at, ended_at, status |
| `MEETING_TRANSCRIPTS` | Regular Table | meeting_id, chunk_number, transcript_text, audio_duration |
| `MEETING_EXTRACTIONS` | Regular Table | meeting_id, chunk_number, raw_json |
| `ACTION_ITEMS` | Hybrid Table | id, meeting_id, owner, task, due_date, status |
| `DECISIONS` | Regular Table | id, meeting_id, decision_text, chunk_number |
