# Progress

## Current Status

**Phase: Planning / Design Complete — No code written yet**

## What's Done

- [x] `projectbrief.md` — full demo design documented
- [x] `productContext.md` — product rationale and UX goals
- [x] `activeContext.md` — current focus and open questions
- [x] `systemPatterns.md` — architecture, data model, key patterns
- [x] `techContext.md` — tech stack and setup requirements
- [x] `progress.md` — this file
- [x] Key decision: `AI_SIMILARITY()` removed from scope

## What's Left to Build

### Snowflake / Data Layer
- [ ] DDL: database, schema, stage (SSE encrypted)
- [ ] DDL: `MEETINGS` hybrid table
- [ ] DDL: `MEETING_TRANSCRIPTS` table
- [ ] DDL: `MEETING_EXTRACTIONS` table
- [ ] DDL: `ACTION_ITEMS` hybrid table
- [ ] DDL: `DECISIONS` table
- [ ] Sample/seed data for demo scenario

### Backend (FastAPI / Python)
- [ ] Project scaffold (`main.py`, requirements, folder structure)
- [ ] Snowflake connection module
- [ ] Audio capture module (PyAudio triple-stream)
- [ ] Stage upload module (PUT command)
- [ ] Transcription module (`ai_transcribe()` invocation)
- [ ] Extraction module (`ai_extract()` with full schema)
- [ ] Upsert logic for ACTION_ITEMS and DECISIONS
- [ ] WebSocket server (push updates to frontend)
- [ ] REST endpoints: POST /meetings/start, POST /meetings/stop, GET /meetings/{id}

### Frontend (React / Vite)
- [ ] Project scaffold
- [ ] WebSocket client hook
- [ ] Recording controls (Start / Stop buttons)
- [ ] Live Transcript panel
- [ ] Action Items panel
- [ ] Decisions panel
- [ ] Key Topics panel
- [ ] Meeting Summary view (post-meeting)
- [ ] Snowflake branding / styling

## Known Issues

None yet — project hasn't started implementation.

## Decision Log

| Date | Decision | Reason |
|---|---|---|
| 2026-07-21 | Remove `AI_SIMILARITY()` | Not needed for this demo scope |
| 2026-07-21 | Adapt from Call Center demo | Reuse proven audio pipeline |
| 2026-07-21 | Use triple-stream audio | Prevents word loss at chunk boundaries |
