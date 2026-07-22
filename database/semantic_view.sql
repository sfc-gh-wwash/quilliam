-- ===============================================
-- Quilliam Semantic View
-- Meeting metadata, action items, and decisions
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA QUILLIAM.STG;

-- Grant required privileges
GRANT CREATE SEMANTIC VIEW ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

CREATE OR REPLACE SEMANTIC VIEW QUILLIAM.STG.MEETING_ANALYTICS_SV
  AS SEMANTIC MODEL
  TABLES (
    QUILLIAM.STG.MEETINGS AS meetings
      PRIMARY KEY (MEETING_ID)
      WITH COLUMNS (
        MEETING_ID DESCRIPTION 'Unique meeting identifier',
        TITLE DESCRIPTION 'Meeting title or name',
        STARTED_AT DESCRIPTION 'When the meeting started',
        ENDED_AT DESCRIPTION 'When the meeting ended',
        STATUS DESCRIPTION 'Meeting status: IN_PROGRESS or COMPLETED',
        NOTES DESCRIPTION 'Free-text notes added by the user',
        SUMMARY DESCRIPTION 'AI-generated meeting summary with overview, decisions, action items, and next steps'
      ),
    QUILLIAM.STG.ACTION_ITEMS AS action_items
      PRIMARY KEY (ID)
      WITH COLUMNS (
        ID DESCRIPTION 'Action item unique ID',
        MEETING_ID DESCRIPTION 'Meeting this action item belongs to',
        OWNER DESCRIPTION 'Person responsible for the action item',
        TASK DESCRIPTION 'Description of the task or to-do',
        DUE_DATE DESCRIPTION 'When the action item is due',
        STATUS DESCRIPTION 'Action item status: OPEN or DONE',
        CREATED_AT DESCRIPTION 'When this action item was extracted'
      ),
    QUILLIAM.STG.DECISIONS AS decisions
      PRIMARY KEY (ID)
      WITH COLUMNS (
        ID DESCRIPTION 'Decision unique ID',
        MEETING_ID DESCRIPTION 'Meeting this decision belongs to',
        DECISION_TEXT DESCRIPTION 'The decision or agreement that was made',
        CREATED_AT DESCRIPTION 'When this decision was extracted'
      )
  )
  RELATIONSHIPS (
    action_items.MEETING_ID REFERENCES meetings.MEETING_ID,
    decisions.MEETING_ID REFERENCES meetings.MEETING_ID
  );

GRANT USAGE ON SEMANTIC VIEW QUILLIAM.STG.MEETING_ANALYTICS_SV TO ROLE QUILLIAM_ADMIN_RL;
GRANT REFERENCES ON SEMANTIC VIEW QUILLIAM.STG.MEETING_ANALYTICS_SV TO ROLE QUILLIAM_ADMIN_RL;
