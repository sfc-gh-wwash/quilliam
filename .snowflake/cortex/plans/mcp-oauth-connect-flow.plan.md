# Plan: MCP OAuth Connect Flow

## Overview

Add a "Connect Services" UI in the agent chat panel that lets users authenticate with Gmail, Google Calendar, and Slack via OAuth before the agent can use those MCP tools. Without this, the agent:run API calls will fail for MCP tools because no user token exists.

## How it works

The OAuth flow for MCP connectors via the Agent:run API requires:
1. `SYSTEM$START_USER_OAUTH_FLOW('<API_INTEGRATION_NAME>')` — returns an auth URL
2. User opens that URL in a browser and consents with the third-party service
3. The third-party redirects to `https://identity.snowflake.com/oauth2/callback` with a query string
4. `SYSTEM$FINISH_OAUTH_FLOW('<query_string>')` — completes the flow in the same Snowflake session

**Key constraint:** Steps 1 and 4 must happen in the **same Snowflake session**. Since the backend maintains a persistent connection via `SnowflakeManager`, this works naturally — the token gets bound to that session/user.

## Architecture

```
Frontend (React)                    Backend (FastAPI)                 Snowflake
─────────────────                   ─────────────────                 ─────────
User clicks "Connect Gmail"
  → POST /api/mcp/connect           → SYSTEM$START_USER_OAUTH_FLOW
                                     ← auth_url                       
  ← { auth_url }
  → window.open(auth_url)           
                                    
[User consents in popup]
[Redirect to identity.snowflake.com/oauth2/callback?code=...&state=...]
[Snowflake redirects to our registered callback with query_string]

  → POST /api/mcp/callback          → SYSTEM$FINISH_OAUTH_FLOW
    { query_string }                 ← success
  ← { success: true }
```

**Note:** The Snowflake OAuth callback (`identity.snowflake.com/oauth2/callback`) handles the provider redirect and then redirects to a URL we don't control. We may need to check if Nova/DCR handles this automatically or if we need a custom redirect. If the callback lands back at a Snowflake-controlled page, the user just closes the popup and we poll for status.

## Implementation

### 1. Backend: `snowflake_manager.py`

Add three methods:
- `get_mcp_connector_status()` — runs `SHOW EXTERNAL MCP SERVERS IN SCHEMA QUILLIAM.STG` and checks which have active user tokens
- `start_mcp_oauth(integration_name)` — calls `SYSTEM$START_USER_OAUTH_FLOW('NOVA_MCP_INTEGRATION')` and returns the URL
- `finish_mcp_oauth(query_string)` — calls `SYSTEM$FINISH_OAUTH_FLOW(query_string)`

### 2. Backend: `api_routes.py`

Add endpoints:
- `GET /api/mcp/connectors` — returns list of connectors with connection status
- `POST /api/mcp/connect` — body: `{ "integration": "NOVA_MCP_INTEGRATION" }`, returns `{ "auth_url": "..." }`
- `POST /api/mcp/callback` — body: `{ "query_string": "..." }`, calls finish flow

### 3. Frontend: `AgentChat.js`

Add a connector status bar above the messages area:
- Shows three pills: Gmail, Calendar, Slack
- Each shows ● Connected (green) or ○ Not Connected (gray)
- A "Connect Services" button that calls `/api/mcp/connect` and opens the auth URL in a popup window
- After the popup closes, poll `/api/mcp/connectors` to refresh status

### 4. Frontend: OAuth callback page

Since the Snowflake identity callback (`identity.snowflake.com/oauth2/callback`) may redirect back with the query string, we need to handle the scenario. Two options:
- **If Snowflake handles it entirely:** The popup lands on a Snowflake success page, user closes it, and the token is already bound to the session.
- **If we need to intercept:** Add a `/oauth/callback` page that reads the URL query string, POSTs it to our backend, and shows "Connected! You can close this window."

Since we're using DCR (`OAUTH_DYNAMIC_CLIENT`), Snowflake's identity service likely handles the full flow. We'll start with option A (just open the popup and poll status after it closes).

## Files Modified

| File | Change |
|------|--------|
| `backend/snowflake_manager.py` | Add OAuth flow methods |
| `backend/api_routes.py` | Add MCP endpoints |
| `frontend/src/AgentChat.js` | Add connector status UI |
| `frontend/src/AgentChat.css` | Style connector pills |
