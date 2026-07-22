# Plan: Agent Chat Panel

## Context

The Quilliam agent (`QUILLIAM.STG.QUILLIAM_AGENT`) is deployed with two tools: transcript search and meeting analytics. The user wants a chat UI embedded in the app with two modes:

1. **Global mode** — available anytime; ask questions across all meetings
2. **Contextual mode** — when a specific meeting is selected, automatically passes the meeting ID as context so questions are scoped to that meeting

The chat will be a slide-out panel on the right side, toggled by a button in the header.

## Architecture

```
Frontend Chat Panel
    → POST /api/agent/chat { message, meeting_id? }
    → Backend calls Snowflake CORTEX.RUN_AGENT()
    → Returns agent response (text + optional SQL results)
    → Displayed in chat panel
```

The backend calls the agent using `SELECT SNOWFLAKE.CORTEX.COMPLETE_AGENT_RUN(...)` or the REST-based `RUN_AGENT` function. When `meeting_id` is provided, the backend prepends context: "The user is asking about meeting {meeting_id}. Focus your search and queries on this specific meeting."

---

## Implementation Steps

### Task 1: Backend — Agent chat endpoint

Add to `api_routes.py`:
- `POST /api/agent/chat` — accepts `{ message: str, meeting_id: str | null }`
- Calls `snowflake_manager.run_agent(message, meeting_id)`

Add to `snowflake_manager.py`:
- `run_agent(message, meeting_id=None)` — builds the prompt (prepending meeting context if provided), calls `SNOWFLAKE.CORTEX.COMPLETE('QUILLIAM.STG.QUILLIAM_AGENT', ...)` or the appropriate agent invocation SQL, returns the response text

### Task 2: Frontend — AgentChat.js component

A slide-out panel component with:
- Chat message history (user messages + agent responses)
- Text input + send button at the bottom
- Mode indicator: "All Meetings" or "Meeting: {title/id}"
- Loading spinner while waiting for response
- Auto-scrolls to latest message

### Task 3: Frontend — Wire into App.js

- Add a chat toggle button in the header (or floating)
- Pass `selectedMeetingId` to `AgentChat` so it knows the context
- Panel slides in/out from the right when toggled

### Task 4: Styling (AgentChat.css)

- Fixed position, right side, full height below header
- ~380px wide
- Backdrop overlay or just push content
- Message bubbles: user (right-aligned, blue) and agent (left-aligned, gray)
- Smooth slide animation

---

## Critical Files

- `backend/api_routes.py` — new POST /api/agent/chat route
- `backend/snowflake_manager.py` — new run_agent method
- `frontend/src/AgentChat.js` — new component
- `frontend/src/AgentChat.css` — styling
- `frontend/src/App.js` — chat toggle button and panel integration
