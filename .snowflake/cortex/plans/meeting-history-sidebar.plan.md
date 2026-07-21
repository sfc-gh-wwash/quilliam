# Plan: Meeting History Sidebar + Editable Notes

## Context

Currently the app is a single-page recorder: start, stop, view live data. Once you leave, there's no way to pull up past meetings. The user wants:

1. A persistent sidebar listing past meetings (title, date)
2. Click a meeting to load its detail: full transcript, action items, decisions, topics, attendees, blockers
3. Users can edit meeting title, manually add/remove action items, edit decisions, and add free-text notes

## Architecture Changes

The app layout changes from single-column to **sidebar + main content**:

```
+---------------------+-------------------------------------------+
| Sidebar             | Main Content                              |
| (meeting list)      | (recorder OR meeting detail view)         |
|                     |                                           |
| [+ New Meeting]     | Live recording panels (current)           |
| - Q3 Planning       |   OR                                      |
| - Sprint Retro      | Past meeting detail (read/edit)            |
| - ...               |                                           |
+---------------------+-------------------------------------------+
```

---

## Implementation Steps

### Task 1: Add `NOTES` column to MEETINGS table + backend `update_meeting` method

- `ALTER TABLE QUILLIAM.STG.MEETINGS ADD COLUMN NOTES VARCHAR(16777216);`
- Add `update_meeting(meeting_id, title, notes)` to `snowflake_manager.py`
- Add `update_action_item(id, owner, task, due_date, status)` and `delete_action_item(id)`
- Add `update_decision(id, text)`, `delete_decision(id)`, `add_decision(meeting_id, text)`
- Add `add_action_item(meeting_id, owner, task, due_date)`

### Task 2: New API routes for meeting history and editing

In `api_routes.py`:

- `GET /meetings` — list all meetings (id, title, started_at, status), ordered by most recent
- `PUT /meetings/{meeting_id}` — update title and notes
- `POST /meetings/{meeting_id}/action-items` — add a new action item
- `PUT /action-items/{id}` — update an action item
- `DELETE /action-items/{id}` — delete an action item
- `POST /meetings/{meeting_id}/decisions` — add a new decision
- `PUT /decisions/{id}` — update a decision
- `DELETE /decisions/{id}` — delete a decision

### Task 3: Refactor frontend layout — sidebar + main area

Change `App.js` to a two-column layout:
- Left: `<Sidebar>` component (list of meetings, "New Meeting" button)
- Right: either `<AudioRecorder>` (live recording mode) or `<MeetingDetail>` (viewing past meeting)

State in App: `selectedMeetingId` — when null, show recorder; when set, show detail.

### Task 4: New `Sidebar.js` component

- Fetches `GET /meetings` on mount
- Renders a scrollable list: meeting title (or "Untitled" fallback), date, status badge
- "New Meeting" button at top resets selection to live recorder
- Active meeting highlighted
- Refreshes list after a meeting ends

### Task 5: New `MeetingDetail.js` component

Shows a past meeting in detail with edit capabilities:
- **Title** — inline editable (click to edit, blur to save)
- **Transcript** — read-only scrollable (same panel as live, but static)
- **Action Items** — table with edit/delete buttons per row + "Add" button at bottom
- **Decisions** — editable list with edit/delete per item + "Add" button
- **Topics / Attendees / Blockers** — read-only tags (from last extraction)
- **Notes** — free-text textarea, auto-saves on blur
- Fetches `GET /meetings/{id}/extractions` and `GET /meetings/{id}/transcript` on load

### Task 6: Styling

- Sidebar: fixed-width left panel (~280px), full height, scrollable
- Active meeting gets highlighted border
- Edit mode uses inline inputs (not separate forms)
- Responsive: sidebar collapses to hamburger on mobile

---

## Critical Files

- `backend/snowflake_manager.py` — new CRUD methods for action_items, decisions, meetings
- `backend/api_routes.py` — new REST endpoints for list/update/delete
- `frontend/src/App.js` — layout refactor to sidebar + main
- `frontend/src/Sidebar.js` — new component
- `frontend/src/MeetingDetail.js` — new component

## Verification

- Start app, record a meeting, stop it
- Click the meeting in the sidebar — detail view loads with transcript, items, decisions
- Edit the title — verify it persists on refresh
- Add/edit/delete action items and decisions — verify in Snowflake
- Type notes, reload — verify notes persist
