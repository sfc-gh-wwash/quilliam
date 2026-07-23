-- ===============================================
-- Meeting Notes Demo DDL
-- Snowflake setup, tables, stage, user/role/warehouse
-- ===============================================

-- ----------------------------------------------------
-- Role, User, Warehouse
-- ----------------------------------------------------
USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS QUILLIAM_ADMIN_RL;
CREATE USER IF NOT EXISTS QUILLIAM_ADMIN
    DEFAULT_ROLE = QUILLIAM_ADMIN_RL
    DEFAULT_WAREHOUSE = QUILLIAM_WH;

GRANT ROLE QUILLIAM_ADMIN_RL TO USER QUILLIAM_ADMIN;

CREATE WAREHOUSE IF NOT EXISTS QUILLIAM_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

GRANT USAGE ON WAREHOUSE QUILLIAM_WH TO ROLE QUILLIAM_ADMIN_RL;

-- ----------------------------------------------------
-- Database & Schema
-- ----------------------------------------------------
CREATE DATABASE IF NOT EXISTS QUILLIAM;
CREATE SCHEMA IF NOT EXISTS QUILLIAM.STG;

GRANT ALL ON DATABASE QUILLIAM TO ROLE QUILLIAM_ADMIN_RL;
GRANT ALL ON SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

USE SCHEMA QUILLIAM.STG;

-- ----------------------------------------------------
-- Stage (SSE encryption required by ai_transcribe)
-- ----------------------------------------------------
CREATE STAGE IF NOT EXISTS QUILLIAM.STG.AUDIO
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

GRANT ALL ON STAGE QUILLIAM.STG.AUDIO TO ROLE QUILLIAM_ADMIN_RL;

-- ----------------------------------------------------
-- MEETINGS — one row per recording session
-- ----------------------------------------------------
CREATE OR REPLACE HYBRID TABLE QUILLIAM.STG.MEETINGS (
    MEETING_ID          VARCHAR(50)     NOT NULL,
    TITLE               VARCHAR(500),
    STARTED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),
    ENDED_AT            TIMESTAMP_NTZ,
    STATUS              VARCHAR(20)     DEFAULT 'IN_PROGRESS',
    NOTES               VARCHAR(16777216),
    SUMMARY             VARCHAR(16777216),

    PRIMARY KEY (MEETING_ID),
    INDEX IDX_MEETINGS_STATUS(STATUS)
);

-- ----------------------------------------------------
-- MEETING_TRANSCRIPTS — one row per audio chunk
-- ----------------------------------------------------
CREATE OR REPLACE TABLE QUILLIAM.STG.MEETING_TRANSCRIPTS (
    ID                  NUMBER(38,0)    NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    MEETING_ID          VARCHAR(50)     NOT NULL,
    CHUNK_NUMBER        NUMBER(10,0)    NOT NULL,
    TRANSCRIPT_TEXT     VARCHAR(16777216),
    AUDIO_DURATION      NUMBER(10,3),
    CREATED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (ID)
);

-- Note: MEETING_TRANSCRIPTS is a regular table; secondary indexes
-- are only supported on Hybrid Tables. Filter by MEETING_ID using
-- standard query predicates instead.

-- ----------------------------------------------------
-- MEETING_EXTRACTIONS — raw ai_extract() JSON per chunk
-- ----------------------------------------------------
CREATE OR REPLACE TABLE QUILLIAM.STG.MEETING_EXTRACTIONS (
    ID                  NUMBER(38,0)    NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    MEETING_ID          VARCHAR(50)     NOT NULL,
    CHUNK_NUMBER        NUMBER(10,0)    NOT NULL,
    RAW_JSON            VARIANT,
    CREATED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (ID)
);

-- Note: MEETING_EXTRACTIONS is a regular table; secondary indexes
-- are only supported on Hybrid Tables.

-- ----------------------------------------------------
-- ACTION_ITEMS — de-duplicated tasks extracted from meeting
-- ----------------------------------------------------
CREATE OR REPLACE HYBRID TABLE QUILLIAM.STG.ACTION_ITEMS (
    ID                  NUMBER(38,0)    NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    MEETING_ID          VARCHAR(50)     NOT NULL,
    OWNER               VARCHAR(200),
    TASK                VARCHAR(2000)   NOT NULL,
    DUE_DATE            VARCHAR(200),
    STATUS              VARCHAR(30)     DEFAULT 'OPEN',
    CREATED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (ID),
    INDEX IDX_ACTIONS_MEETING(MEETING_ID),
    INDEX IDX_ACTIONS_STATUS(STATUS)
);

-- ----------------------------------------------------
-- DECISIONS — conclusions captured from meeting
-- ----------------------------------------------------
CREATE OR REPLACE TABLE QUILLIAM.STG.DECISIONS (
    ID                  NUMBER(38,0)    NOT NULL AUTOINCREMENT START 1 INCREMENT 1 NOORDER,
    MEETING_ID          VARCHAR(50)     NOT NULL,
    DECISION_TEXT       VARCHAR(4000)   NOT NULL,
    CHUNK_NUMBER        NUMBER(10,0),
    CREATED_AT          TIMESTAMP_NTZ   DEFAULT CURRENT_TIMESTAMP(),

    PRIMARY KEY (ID)
);

-- Note: DECISIONS is a regular table; secondary indexes
-- are only supported on Hybrid Tables.

-- ----------------------------------------------------
-- Grants on tables
-- ----------------------------------------------------
GRANT ALL ON ALL TABLES IN SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;
GRANT ALL ON FUTURE TABLES IN SCHEMA QUILLIAM.STG TO ROLE QUILLIAM_ADMIN_RL;

-- ----------------------------------------------------
-- Cortex AI function access
-- ----------------------------------------------------
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE QUILLIAM_ADMIN_RL;

-- ----------------------------------------------------
-- Key pair auth for QUILLIAM_ADMIN
-- (run separately after generating rsa_key.p8)
-- ALTER USER QUILLIAM_ADMIN SET RSA_PUBLIC_KEY='<paste public key>';
-- ----------------------------------------------------

COMMENT ON TABLE QUILLIAM.STG.MEETINGS IS 'One row per meeting recording session';
COMMENT ON TABLE QUILLIAM.STG.MEETING_TRANSCRIPTS IS 'Chunked transcripts from ai_transcribe()';
COMMENT ON TABLE QUILLIAM.STG.MEETING_EXTRACTIONS IS 'Raw ai_extract() JSON output per chunk';
COMMENT ON TABLE QUILLIAM.STG.ACTION_ITEMS IS 'Action items extracted from meetings';
COMMENT ON TABLE QUILLIAM.STG.DECISIONS IS 'Decisions captured from meetings';
