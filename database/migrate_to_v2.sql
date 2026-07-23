-- ===============================================
-- Quilliam Migration Script
-- Converts hybrid tables to regular tables,
-- widens MEETING_ID, adds NOTES/SUMMARY columns,
-- and creates Cortex Search Services + Agent.
--
-- Safe to run on an existing QUILLIAM database.
-- Preserves all existing data.
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA QUILLIAM.STG;

-- =============================================
-- 1. MEETINGS: Hybrid Table → Regular Table
--    Also widens MEETING_ID and ensures NOTES/SUMMARY exist
-- =============================================

-- Clone preserves data with zero-copy and is instant
CREATE TABLE IF NOT EXISTS QUILLIAM.STG.MEETINGS_MIGRATION_BACKUP
  CLONE QUILLIAM.STG.MEETINGS;

DROP TABLE IF EXISTS QUILLIAM.STG.MEETINGS;

CREATE TABLE QUILLIAM.STG.MEETINGS (
    MEETING_ID          VARCHAR(100)    NOT NULL,
    TITLE               VARCHAR(500),
    STARTED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    ENDED_AT            TIMESTAMP_NTZ,
    STATUS              VARCHAR(20)     DEFAULT 'IN_PROGRESS',
    NOTES               VARCHAR(16777216),
    SUMMARY             VARCHAR(16777216),
    PRIMARY KEY (MEETING_ID)
);

-- Restore data (handles both old schema without NOTES/SUMMARY and new schema with them)
INSERT INTO QUILLIAM.STG.MEETINGS (MEETING_ID, TITLE, STARTED_AT, ENDED_AT, STATUS, NOTES, SUMMARY)
SELECT
    MEETING_ID,
    TITLE,
    STARTED_AT,
    ENDED_AT,
    STATUS,
    TRY_CAST(NOTES AS VARCHAR) AS NOTES,
    TRY_CAST(SUMMARY AS VARCHAR) AS SUMMARY
FROM QUILLIAM.STG.MEETINGS_MIGRATION_BACKUP;

DROP TABLE QUILLIAM.STG.MEETINGS_MIGRATION_BACKUP;

-- =============================================
-- 2. ACTION_ITEMS: Hybrid Table → Regular Table
-- =============================================

CREATE TABLE IF NOT EXISTS QUILLIAM.STG.ACTION_ITEMS_MIGRATION_BACKUP
  CLONE QUILLIAM.STG.ACTION_ITEMS;

DROP TABLE IF EXISTS QUILLIAM.STG.ACTION_ITEMS;

CREATE TABLE QUILLIAM.STG.ACTION_ITEMS (
    ID                  NUMBER(38,0)    NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    MEETING_ID          VARCHAR(100)    NOT NULL,
    OWNER               VARCHAR(200),
    TASK                VARCHAR(2000)   NOT NULL,
    DUE_DATE            VARCHAR(200),
    STATUS              VARCHAR(30)     DEFAULT 'OPEN',
    CREATED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (ID)
);

INSERT INTO QUILLIAM.STG.ACTION_ITEMS (ID, MEETING_ID, OWNER, TASK, DUE_DATE, STATUS, CREATED_AT)
SELECT ID, MEETING_ID, OWNER, TASK, DUE_DATE, STATUS, CREATED_AT
FROM QUILLIAM.STG.ACTION_ITEMS_MIGRATION_BACKUP;

DROP TABLE QUILLIAM.STG.ACTION_ITEMS_MIGRATION_BACKUP;

-- =============================================
-- 3. Widen MEETING_ID on other tables (50 → 100)
-- =============================================

ALTER TABLE QUILLIAM.STG.MEETING_TRANSCRIPTS ALTER COLUMN MEETING_ID SET DATA TYPE VARCHAR(100);
ALTER TABLE QUILLIAM.STG.MEETING_EXTRACTIONS ALTER COLUMN MEETING_ID SET DATA TYPE VARCHAR(100);
ALTER TABLE QUILLIAM.STG.DECISIONS ALTER COLUMN MEETING_ID SET DATA TYPE VARCHAR(100);

-- =============================================
-- 4. Re-grant table access
-- =============================================

GRANT ALL ON ALL TABLES IN SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

-- =============================================
-- 5. Create Cortex Search Services
-- =============================================

GRANT CREATE CORTEX SEARCH SERVICE ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

-- Transcript search
CREATE OR REPLACE CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_TRANSCRIPT_SEARCH
  ON TRANSCRIPT_TEXT
  ATTRIBUTES MEETING_ID
  WAREHOUSE = QUILLIAM_WH
  TARGET_LAG = '15 minute'
  AS (
    SELECT MEETING_ID, TRANSCRIPT_TEXT
    FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
    WHERE CHUNK_NUMBER = 0
      AND TRANSCRIPT_TEXT IS NOT NULL
      AND LENGTH(TRIM(TRANSCRIPT_TEXT)) > 10
  );

-- Notes search
CREATE OR REPLACE CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_NOTES_SEARCH
  ON NOTES
  ATTRIBUTES MEETING_ID, TITLE
  WAREHOUSE = QUILLIAM_WH
  TARGET_LAG = '15 minute'
  AS (
    SELECT MEETING_ID, TITLE, NOTES
    FROM QUILLIAM.STG.MEETINGS
    WHERE NOTES IS NOT NULL
      AND LENGTH(TRIM(NOTES)) > 10
  );

-- Summary search
CREATE OR REPLACE CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_SUMMARY_SEARCH
  ON SUMMARY
  ATTRIBUTES MEETING_ID, TITLE
  WAREHOUSE = QUILLIAM_WH
  TARGET_LAG = '15 minute'
  AS (
    SELECT MEETING_ID, TITLE, SUMMARY
    FROM QUILLIAM.STG.MEETINGS
    WHERE SUMMARY IS NOT NULL
      AND LENGTH(TRIM(SUMMARY)) > 10
  );

GRANT USAGE ON CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_TRANSCRIPT_SEARCH TO ROLE QUILLIAM_ADMIN_RL;
GRANT USAGE ON CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_NOTES_SEARCH TO ROLE QUILLIAM_ADMIN_RL;
GRANT USAGE ON CORTEX SEARCH SERVICE QUILLIAM.STG.MEETING_SUMMARY_SEARCH TO ROLE QUILLIAM_ADMIN_RL;

-- =============================================
-- 6. Recreate Agent with all search tools
-- =============================================

GRANT CREATE AGENT ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

CREATE OR REPLACE AGENT QUILLIAM.STG.QUILLIAM_AGENT
FROM SPECIFICATION $$
{
  "models": {
    "orchestration": "auto"
  },
  "orchestration": {
    "budget": {
      "seconds": 900,
      "tokens": 400000
    }
  },
  "instructions": {
    "orchestration": "You are Quilliam, an AI meeting assistant. You have access to meeting transcripts, meeting notes, meeting summaries, and structured meeting data (action items, decisions, metadata). Use the transcript search tool when users ask about what was discussed verbatim or who said what. Use the notes search tool when users want to find detailed meeting content including action items, decisions, and meeting flow. Use the summary search tool for quick high-level overviews of what meetings covered. Use the meeting analytics tool when users ask about action items, decisions, meeting dates, statuses, or want structured data queries. Always be helpful and reference specific meetings when possible.",
    "response": "Be concise and structured. When referencing meeting content, include the meeting title. Format action items as bullet lists with owners. If searching transcripts or notes, quote relevant portions."
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "search_transcripts",
        "description": "Search across all meeting transcripts to find verbatim discussions, statements, or context from past meetings. Use this when the user asks about what was said word-for-word or who discussed what."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "search_meeting_notes",
        "description": "Search across full meeting notes including meeting flow, action items, decisions, and open questions. Use this when the user wants detailed context about what happened in a meeting, who has action items, or what decisions were made."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "search_meeting_summaries",
        "description": "Search across concise meeting summaries for quick high-level overviews. Use this when the user wants a brief understanding of what a meeting was about or to find meetings related to a topic."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "query_meetings",
        "description": "Query structured meeting data including meeting metadata (titles, dates, status, summaries), action items (owner, task, due date, status), and decisions. Use this for questions about action items, decisions, meeting counts, timelines, or any structured data queries."
      }
    }
  ],
  "tool_resources": {
    "search_transcripts": {
      "execution_environment": {
        "query_timeout": 299,
        "type": "warehouse",
        "warehouse": "QUILLIAM_WH"
      },
      "search_service": "QUILLIAM.STG.MEETING_TRANSCRIPT_SEARCH"
    },
    "search_meeting_notes": {
      "execution_environment": {
        "query_timeout": 299,
        "type": "warehouse",
        "warehouse": "QUILLIAM_WH"
      },
      "search_service": "QUILLIAM.STG.MEETING_NOTES_SEARCH"
    },
    "search_meeting_summaries": {
      "execution_environment": {
        "query_timeout": 299,
        "type": "warehouse",
        "warehouse": "QUILLIAM_WH"
      },
      "search_service": "QUILLIAM.STG.MEETING_SUMMARY_SEARCH"
    },
    "query_meetings": {
      "execution_environment": {
        "query_timeout": 299,
        "type": "warehouse",
        "warehouse": "QUILLIAM_WH"
      },
      "semantic_view": "QUILLIAM.STG.MEETING_ANALYTICS_SV"
    }
  }
}
$$;

GRANT USAGE ON AGENT QUILLIAM.STG.QUILLIAM_AGENT TO ROLE QUILLIAM_ADMIN_RL;

-- =============================================
-- 7. Cleanup
-- =============================================

DROP TABLE IF EXISTS QUILLIAM.STG.MEETINGS_SEARCH_SOURCE;
DROP VIEW IF EXISTS QUILLIAM.STG.MEETINGS_FOR_SEARCH;

-- =============================================
-- Done. Verify:
-- =============================================
SELECT 'MEETINGS' AS object, COUNT(*) AS rows FROM QUILLIAM.STG.MEETINGS
UNION ALL
SELECT 'ACTION_ITEMS', COUNT(*) FROM QUILLIAM.STG.ACTION_ITEMS
UNION ALL
SELECT 'TRANSCRIPTS', COUNT(*) FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
UNION ALL
SELECT 'EXTRACTIONS', COUNT(*) FROM QUILLIAM.STG.MEETING_EXTRACTIONS
UNION ALL
SELECT 'DECISIONS', COUNT(*) FROM QUILLIAM.STG.DECISIONS;

SHOW CORTEX SEARCH SERVICES IN SCHEMA QUILLIAM.STG;
SHOW AGENTS IN SCHEMA QUILLIAM.STG;
