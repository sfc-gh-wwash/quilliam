-- ===============================================
-- Quilliam Semantic View
-- Meeting metadata, action items, and decisions
-- ===============================================

USE ROLE ACCOUNTADMIN;
USE SCHEMA QUILLIAM.STG;

-- Grant required privileges
GRANT CREATE SEMANTIC VIEW ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

CREATE OR REPLACE SEMANTIC VIEW QUILLIAM.STG.MEETING_ANALYTICS_SV

  TABLES (
    meetings AS QUILLIAM.STG.MEETINGS
      PRIMARY KEY (MEETING_ID)
      COMMENT = 'One row per meeting recording session',
    action_items AS QUILLIAM.STG.ACTION_ITEMS
      PRIMARY KEY (ID)
      COMMENT = 'Action items extracted from meetings',
    decisions AS QUILLIAM.STG.DECISIONS
      PRIMARY KEY (ID)
      COMMENT = 'Decisions captured from meetings'
  )

  RELATIONSHIPS (
    action_items_to_meetings AS
      action_items (MEETING_ID) REFERENCES meetings (MEETING_ID),
    decisions_to_meetings AS
      decisions (MEETING_ID) REFERENCES meetings (MEETING_ID)
  )

  DIMENSIONS (
    meetings.meeting_id_dim AS MEETING_ID
      COMMENT = 'Unique meeting identifier',
    meetings.title_dim AS TITLE
      COMMENT = 'Meeting title or name',
    meetings.started_at_dim AS STARTED_AT
      COMMENT = 'When the meeting started',
    meetings.ended_at_dim AS ENDED_AT
      COMMENT = 'When the meeting ended',
    meetings.status_dim AS STATUS
      COMMENT = 'Meeting status: IN_PROGRESS or COMPLETED'
      SAMPLE_VALUES ('IN_PROGRESS', 'COMPLETED')
      IS_ENUM,
    action_items.owner_dim AS OWNER
      COMMENT = 'Person responsible for the action item',
    action_items.task_dim AS TASK
      COMMENT = 'Description of the task or to-do',
    action_items.due_date_dim AS DUE_DATE
      COMMENT = 'When the action item is due',
    action_items.action_status_dim AS STATUS
      COMMENT = 'Action item status: OPEN or DONE'
      SAMPLE_VALUES ('OPEN', 'DONE')
      IS_ENUM,
    decisions.decision_text_dim AS DECISION_TEXT
      COMMENT = 'The decision or agreement that was made'
  )

  METRICS (
    meetings.meeting_count AS COUNT(MEETING_ID)
      COMMENT = 'Total number of meetings',
    action_items.action_item_count AS COUNT(ID)
      COMMENT = 'Total number of action items',
    action_items.open_action_items AS COUNT(CASE WHEN STATUS = 'OPEN' THEN 1 END)
      COMMENT = 'Number of open action items',
    decisions.decision_count AS COUNT(ID)
      COMMENT = 'Total number of decisions'
  )

  COMMENT = 'Semantic view for meeting analytics - meetings, action items, and decisions';

-- Grant access
GRANT REFERENCES, SELECT ON SEMANTIC VIEW QUILLIAM.STG.MEETING_ANALYTICS_SV TO ROLE QUILLIAM_ADMIN_RL;
