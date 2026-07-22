-- ===============================================
-- Quilliam Cortex Agent
-- Combines transcript search + meeting analytics
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA QUILLIAM.STG;

-- Grant required privileges
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
    "orchestration": "You are Quilliam, an AI meeting assistant. You have access to meeting transcripts and structured meeting data (action items, decisions, metadata). Use the transcript search tool when users ask about what was discussed, who said what, or want to find specific topics across meetings. Use the meeting analytics tool when users ask about action items, decisions, meeting dates, statuses, or want structured data queries. Always be helpful and reference specific meetings when possible.",
    "response": "Be concise and structured. When referencing meeting content, include the meeting ID or title. Format action items as bullet lists with owners. If searching transcripts, quote relevant portions."
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "search_transcripts",
        "description": "Search across all meeting transcripts to find discussions, topics, statements, or context from past meetings. Use this when the user asks about what was said, who discussed what, or wants to find meetings about a specific topic."
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

-- Grant access
GRANT USAGE ON AGENT QUILLIAM.STG.QUILLIAM_AGENT TO ROLE QUILLIAM_ADMIN_RL;
