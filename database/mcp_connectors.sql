-- ===============================================
-- MCP Connector Setup: Gmail, Google Calendar, Slack
-- Uses Snowflake-managed Nova/Natoma endpoints (DCR)
-- No external OAuth credentials required.
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA QUILLIAM.STG;

-- Grant required privileges
GRANT CREATE EXTERNAL MCP SERVER ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

-- =============================================
-- 1. API Integration (shared, DCR via Nova)
-- =============================================

CREATE OR REPLACE API INTEGRATION nova_mcp_integration
  API_PROVIDER = EXTERNAL_MCP
  API_ALLOWED_PREFIXES = (
    'https://snowflake.mcp.nova.cortex.snowflake.app'
  )
  API_USER_AUTHENTICATION = (
    TYPE = OAUTH_DYNAMIC_CLIENT,
    OAUTH_RESOURCE_URL = 'https://snowflake.mcp.nova.cortex.snowflake.app'
  )
  ENABLED = TRUE;

-- =============================================
-- 2. Gmail External MCP Server
-- =============================================

CREATE OR REPLACE EXTERNAL MCP SERVER QUILLIAM.STG.GMAIL_MCP
  WITH DISPLAY_NAME = 'Gmail'
  URL = 'https://snowflake.mcp.nova.cortex.snowflake.app/v2/profile/default-profile/google-gmail/mcp'
  API_INTEGRATION = nova_mcp_integration;

-- =============================================
-- 3. Google Calendar External MCP Server
-- =============================================

CREATE OR REPLACE EXTERNAL MCP SERVER QUILLIAM.STG.GOOGLE_CALENDAR_MCP
  WITH DISPLAY_NAME = 'Google Calendar'
  URL = 'https://snowflake.mcp.nova.cortex.snowflake.app/v2/profile/default-profile/google-calendar/mcp'
  API_INTEGRATION = nova_mcp_integration;

-- =============================================
-- 4. Slack External MCP Server
-- =============================================

CREATE OR REPLACE EXTERNAL MCP SERVER QUILLIAM.STG.SLACK_MCP
  WITH DISPLAY_NAME = 'Slack'
  URL = 'https://snowflake.mcp.nova.cortex.snowflake.app/v2/profile/default-profile/slack-remote/mcp'
  API_INTEGRATION = nova_mcp_integration;

-- =============================================
-- 5. Grant access
-- =============================================

GRANT USAGE ON INTEGRATION nova_mcp_integration TO ROLE QUILLIAM_ADMIN_RL;
GRANT USAGE ON EXTERNAL MCP SERVER QUILLIAM.STG.GMAIL_MCP TO ROLE QUILLIAM_ADMIN_RL;
GRANT USAGE ON EXTERNAL MCP SERVER QUILLIAM.STG.GOOGLE_CALENDAR_MCP TO ROLE QUILLIAM_ADMIN_RL;
GRANT USAGE ON EXTERNAL MCP SERVER QUILLIAM.STG.SLACK_MCP TO ROLE QUILLIAM_ADMIN_RL;

-- =============================================
-- 6. Add to Quilliam Agent (via mcp_servers in spec)
-- =============================================
-- MCP servers are included in the agent specification's "mcp_servers" array.
-- See cortex_agent.sql for the full agent spec.
-- The syntax is:
--   "mcp_servers": [
--     {"server_spec": {"name": "QUILLIAM.STG.GMAIL_MCP"}},
--     {"server_spec": {"name": "QUILLIAM.STG.GOOGLE_CALENDAR_MCP"}},
--     {"server_spec": {"name": "QUILLIAM.STG.SLACK_MCP"}}
--   ]

-- =============================================
-- Verify
-- =============================================

SHOW EXTERNAL MCP SERVERS IN SCHEMA QUILLIAM.STG;
