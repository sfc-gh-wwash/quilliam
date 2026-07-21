# Active Context

## Current Focus

Coding complete. Need to provision Snowflake objects and do an end-to-end test.

## What Was Just Done

- Rewrote all 8 files from call center to meeting notes
- New DDL: `database/meeting_notes_ddl.sql` (MEETINGS, MEETING_TRANSCRIPTS, MEETING_EXTRACTIONS, ACTION_ITEMS, DECISIONS)
- Backend: new `snowflake_manager.py`, `audio_recorder.py`, `api_routes.py`, `main.py`
- Frontend: new `AudioRecorder.js` (live transcript, action items, decisions, tags, blockers panels) + `AudioRecorder.css`

## Next Steps

1. Run `database/meeting_notes_ddl.sql` in Snowflake to create all objects
2. Generate RSA key for MEETING_NOTES_ADMIN and run: `ALTER USER MEETING_NOTES_ADMIN SET RSA_PUBLIC_KEY='...'`
3. Copy new RSA key to `backend/rsa_key.p8`
4. Restart backend and frontend
5. Test end-to-end: start recording → verify transcription → verify extraction → verify UI panels update
