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
  },
  "mcp_servers": [
    {"server_spec": {"name": "QUILLIAM.STG.GMAIL_MCP"}},
    {"server_spec": {"name": "QUILLIAM.STG.GOOGLE_CALENDAR_MCP"}},
    {"server_spec": {"name": "QUILLIAM.STG.SLACK_MCP"}}
  ]
}
$$;

-- Grant access
GRANT USAGE ON AGENT QUILLIAM.STG.QUILLIAM_AGENT TO ROLE QUILLIAM_ADMIN_RL;
