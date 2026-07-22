import os
import asyncio
import time
import requests
from typing import Optional, Dict, Any, List
import snowflake.connector
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class SnowflakeManager:
    def __init__(self):
        load_dotenv(dotenv_path="../.env")
        self.connection: Optional[snowflake.connector.SnowflakeConnection] = None
        self.cursor: Optional[snowflake.connector.cursor.SnowflakeCursor] = None

        private_key_path = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH', './rsa_key.p8')
        with open(private_key_path, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'private_key': private_key_bytes,
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA'),
            'role': os.getenv('SNOWFLAKE_ROLE'),
        }

        required_fields = ['account', 'user']
        missing_fields = [field for field in required_fields if not self.config[field]]
        if missing_fields:
            raise ValueError(f"Missing required Snowflake configuration: {missing_fields}")

    async def connect(self) -> None:
        try:
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(
                None, lambda: snowflake.connector.connect(**self.config)
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to Snowflake: {self.config['account']}")
        except Exception as e:
            print(f"Failed to connect to Snowflake: {str(e)}")
            raise

    async def disconnect(self) -> None:
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("Disconnected from Snowflake")
        except Exception as e:
            print(f"Error during Snowflake disconnect: {str(e)}")

    def is_connected(self) -> bool:
        try:
            if not self.connection:
                return False
            self.cursor.execute("SELECT 1")
            return True
        except:
            return False

    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list:
        try:
            loop = asyncio.get_event_loop()
            if params:
                await loop.run_in_executor(None, self.cursor.execute, query, params)
            else:
                await loop.run_in_executor(None, self.cursor.execute, query)
            results = await loop.run_in_executor(None, self.cursor.fetchall)
            return results
        except Exception as e:
            print(f"Query execution failed: {str(e)}")
            raise

    # ------------------------------------------------------------------
    # Meeting ID generation
    # ------------------------------------------------------------------

    async def generate_meeting_id(self) -> str:
        timestamp = str(int(time.time() * 1000))
        return f"MTG{timestamp[-10:]}"

    # ------------------------------------------------------------------
    # Stage upload (unchanged from call center — only stage path changes)
    # ------------------------------------------------------------------

    async def upload_mp3_to_stage(self, file_path: str, stage_name: str = "@QUILLIAM.STG.AUDIO") -> str:
        try:
            put_query = f"PUT file://{file_path} {stage_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
            await self.execute_query(put_query)
            filename = os.path.basename(file_path)
            return f"{stage_name}/{filename}"
        except Exception as e:
            print(f"MP3 upload failed: {str(e)}")
            raise

    # ------------------------------------------------------------------
    # Transcription: insert one chunk into MEETING_TRANSCRIPTS
    # ------------------------------------------------------------------

    async def process_audio_transcription(self, filename: str) -> bool:
        try:
            file_basename = filename.split('/')[-1]

            transcription_sql = f"""
            INSERT INTO QUILLIAM.STG.MEETING_TRANSCRIPTS
                (MEETING_ID, CHUNK_NUMBER, TRANSCRIPT_TEXT, AUDIO_DURATION, CREATED_AT)
            WITH t AS (
                SELECT
                    ai_transcribe(to_file('@QUILLIAM.STG.AUDIO', '{file_basename}')) AS transcription,
                    '{file_basename}' AS filename
            )
            SELECT
                split_part(filename, '_', 1)                       AS MEETING_ID,
                TRY_TO_NUMBER(split_part(filename, '_', 2))        AS CHUNK_NUMBER,
                transcription:text::TEXT                           AS TRANSCRIPT_TEXT,
                transcription:audio_duration::FLOAT                AS AUDIO_DURATION,
                CURRENT_TIMESTAMP()                                AS CREATED_AT
            FROM t
            WHERE transcription:text::TEXT IS NOT NULL
              AND LENGTH(TRIM(transcription:text::TEXT)) > 0
            """

            await self.execute_query(transcription_sql)
            print(f"Transcription processed for: {file_basename}")

            parts = file_basename.split('_')
            if len(parts) >= 2:
                meeting_id = parts[0]
                await self.detect_questions(meeting_id)

            return True
        except Exception as e:
            print(f"Transcription processing failed for {filename}: {str(e)}")
            return False

    # ------------------------------------------------------------------
    # Real-time question detection (last 3 chunks)
    # ------------------------------------------------------------------

    async def detect_questions(self, meeting_id: str) -> list:
        """Detect questions from the last 3 transcript chunks using ai_extract."""
        try:
            detection_sql = f"""
            WITH recent AS (
                SELECT LISTAGG(TRANSCRIPT_TEXT, ' ') WITHIN GROUP (ORDER BY CHUNK_NUMBER) AS text_block
                FROM (
                    SELECT TRANSCRIPT_TEXT, CHUNK_NUMBER
                    FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
                    WHERE MEETING_ID = '{meeting_id}'
                      AND CHUNK_NUMBER > 0
                      AND LENGTH(TRIM(TRANSCRIPT_TEXT)) > 3
                    ORDER BY CHUNK_NUMBER DESC
                    LIMIT 3
                )
            )
            SELECT ai_extract(
                text => text_block,
                responseformat => PARSE_JSON('{{"questions": "List any questions that were asked in this conversation. Return an empty list if no questions were asked."}}')
            ) AS result
            FROM recent
            WHERE text_block IS NOT NULL AND LENGTH(text_block) > 10
            """

            results = await self.execute_query(detection_sql)
            if results and results[0][0]:
                import json
                parsed = json.loads(results[0][0]) if isinstance(results[0][0], str) else results[0][0]
                response = parsed.get('response', {})
                questions = response.get('questions', [])
                if isinstance(questions, str):
                    questions = [questions] if questions and questions != 'None' else []
                questions = [q for q in questions if q and str(q) not in ('None', '')]
                return questions
            return []
        except Exception as e:
            print(f"Question detection failed for {meeting_id}: {str(e)}")
            return []

    # ------------------------------------------------------------------
    # Extraction: run ai_extract() on full meeting transcript (at meeting end)
    # ------------------------------------------------------------------

    async def extract_meeting_notes(self, meeting_id: str) -> bool:
        try:
            extraction_sql = f"""
            INSERT INTO QUILLIAM.STG.MEETING_EXTRACTIONS
                (MEETING_ID, CHUNK_NUMBER, RAW_JSON, CREATED_AT)
            WITH transcript AS (
                SELECT
                    MEETING_ID,
                    MAX(CHUNK_NUMBER) AS latest_chunk,
                    LISTAGG(TRANSCRIPT_TEXT, ' ') WITHIN GROUP (ORDER BY CHUNK_NUMBER) AS full_text
                FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
                WHERE MEETING_ID = '{meeting_id}'
                  AND LENGTH(TRIM(TRANSCRIPT_TEXT)) > 3
                GROUP BY MEETING_ID
            ),
            extracted AS (
                SELECT
                    MEETING_ID,
                    latest_chunk,
                    ai_extract(
                        text => full_text,
                        responseformat => PARSE_JSON('{{
                            "attendees": "List of people mentioned or introduced by name",
                            "action_items": "List of tasks or to-dos, each with owner and due date if mentioned",
                            "decisions": "List of conclusions or agreements reached",
                            "topics": "List of high-level themes or agenda items discussed",
                            "key_dates": "List of deadlines, milestones, or specific dates referenced",
                            "blockers": "List of risks, concerns, or issues flagged",
                            "follow_ups": "List of things to revisit or schedule later",
                            "meeting_title": "Inferred short title for the meeting based on topics"
                        }}')
                    ) AS parsed
                FROM transcript
            )
            SELECT
                MEETING_ID,
                latest_chunk,
                parsed:response AS RAW_JSON,
                CURRENT_TIMESTAMP()
            FROM extracted
            WHERE parsed:response IS NOT NULL
            """

            await self.execute_query(extraction_sql)
            print(f"Meeting notes extraction completed for meeting {meeting_id}")

            await self._upsert_action_items(meeting_id)

            return True
        except Exception as e:
            print(f"Meeting notes extraction failed for {meeting_id}: {str(e)}")
            return False

    async def _upsert_action_items(self, meeting_id: str) -> None:
        """Insert new action items from the latest extraction, skipping duplicates."""
        try:
            upsert_sql = f"""
            INSERT INTO QUILLIAM.STG.ACTION_ITEMS
                (MEETING_ID, OWNER, TASK, DUE_DATE, STATUS, CREATED_AT)
            WITH latest AS (
                SELECT RAW_JSON
                FROM QUILLIAM.STG.MEETING_EXTRACTIONS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY CREATED_AT DESC
                LIMIT 1
            ),
            items AS (
                SELECT
                    '{meeting_id}'                      AS MEETING_ID,
                    item.value:owner::TEXT              AS OWNER,
                    item.value:task::TEXT               AS TASK,
                    item.value:due_date::TEXT           AS DUE_DATE
                FROM latest,
                     LATERAL FLATTEN(input => latest.RAW_JSON:action_items) item
                WHERE item.value:task::TEXT IS NOT NULL
                  AND TRIM(item.value:task::TEXT) != ''
                  AND item.value:task::TEXT != 'None'
            )
            SELECT i.MEETING_ID, i.OWNER, i.TASK, i.DUE_DATE, 'OPEN', CURRENT_TIMESTAMP()
            FROM items i
            LEFT JOIN QUILLIAM.STG.ACTION_ITEMS existing
                ON existing.MEETING_ID = i.MEETING_ID
               AND existing.TASK = i.TASK
            WHERE existing.ID IS NULL
            """
            await self.execute_query(upsert_sql)
        except Exception as e:
            print(f"Action item upsert failed for {meeting_id}: {str(e)}")

    async def _upsert_decisions(self, meeting_id: str) -> None:
        """Insert new decisions from the latest extraction, skipping duplicates."""
        try:
            upsert_sql = f"""
            INSERT INTO QUILLIAM.STG.DECISIONS
                (MEETING_ID, DECISION_TEXT, CHUNK_NUMBER, CREATED_AT)
            WITH latest AS (
                SELECT RAW_JSON, CHUNK_NUMBER
                FROM QUILLIAM.STG.MEETING_EXTRACTIONS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY CREATED_AT DESC
                LIMIT 1
            ),
            items AS (
                SELECT
                    '{meeting_id}'              AS MEETING_ID,
                    d.value::TEXT               AS DECISION_TEXT,
                    latest.CHUNK_NUMBER
                FROM latest,
                     LATERAL FLATTEN(input => latest.RAW_JSON:decisions) d
                WHERE d.value::TEXT IS NOT NULL
                  AND TRIM(d.value::TEXT) != ''
                  AND d.value::TEXT != 'None'
            )
            SELECT i.MEETING_ID, i.DECISION_TEXT, i.CHUNK_NUMBER, CURRENT_TIMESTAMP()
            FROM items i
            LEFT JOIN QUILLIAM.STG.DECISIONS existing
                ON existing.MEETING_ID = i.MEETING_ID
               AND existing.DECISION_TEXT = i.DECISION_TEXT
            WHERE existing.ID IS NULL
            """
            await self.execute_query(upsert_sql)
        except Exception as e:
            print(f"Decision upsert failed for {meeting_id}: {str(e)}")

    # ------------------------------------------------------------------
    # Read methods for API routes
    # ------------------------------------------------------------------

    async def get_meeting_extractions(self, meeting_id: str) -> Dict[str, Any]:
        """Return aggregated extractions for a meeting: action_items, decisions, topics, attendees, blockers."""
        try:
            action_items = await self.execute_query(f"""
                SELECT ID, OWNER, TASK, DUE_DATE, STATUS
                FROM QUILLIAM.STG.ACTION_ITEMS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY ID
            """)

            decisions = await self.execute_query(f"""
                SELECT ID, DECISION_TEXT
                FROM QUILLIAM.STG.DECISIONS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY ID
            """)

            # Topics, attendees, blockers, follow_ups, meeting_title from latest extraction
            latest = await self.execute_query(f"""
                SELECT RAW_JSON
                FROM QUILLIAM.STG.MEETING_EXTRACTIONS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY CREATED_AT DESC
                LIMIT 1
            """)

            raw = {}
            if latest and latest[0][0]:
                import json
                raw = json.loads(latest[0][0]) if isinstance(latest[0][0], str) else latest[0][0]

            def to_list(val):
                if isinstance(val, list):
                    return [str(v) for v in val if v and str(v) not in ('None', '')]
                if val:
                    return [str(val)]
                return []

            return {
                'meeting_id': meeting_id,
                'action_items': [
                    {'id': r[0], 'owner': r[1], 'task': r[2], 'due_date': r[3], 'status': r[4]}
                    for r in action_items
                ],
                'decisions': [{'id': r[0], 'text': r[1]} for r in decisions],
                'topics': to_list(raw.get('topics')),
                'attendees': to_list(raw.get('attendees')),
                'blockers': to_list(raw.get('blockers')),
                'follow_ups': to_list(raw.get('follow_ups')),
                'meeting_title': raw.get('meeting_title', ''),
            }
        except Exception as e:
            print(f"get_meeting_extractions failed for {meeting_id}: {str(e)}")
            return {
                'meeting_id': meeting_id,
                'action_items': [], 'decisions': [], 'topics': [],
                'attendees': [], 'blockers': [], 'follow_ups': [], 'meeting_title': ''
            }

    async def get_meeting_transcript(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Return ordered transcript chunks for a meeting."""
        try:
            results = await self.execute_query(f"""
                SELECT CHUNK_NUMBER, TRANSCRIPT_TEXT, AUDIO_DURATION, CREATED_AT
                FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
                WHERE MEETING_ID = '{meeting_id}'
                ORDER BY CHUNK_NUMBER
            """)
            return [
                {
                    'chunk_number': r[0],
                    'text': r[1],
                    'audio_duration': float(r[2]) if r[2] else None,
                    'created_at': str(r[3]) if r[3] else None,
                }
                for r in results
            ]
        except Exception as e:
            print(f"get_meeting_transcript failed for {meeting_id}: {str(e)}")
            return []

    async def close_meeting(self, meeting_id: str) -> bool:
        """Mark a meeting as completed, run full extraction, speaker transcription, and generate summary."""
        try:
            await self._transcribe_archive_with_speakers(meeting_id)
            await self.extract_meeting_notes(meeting_id)
            await self._upsert_decisions(meeting_id)
            await self._generate_summary(meeting_id)
            await self.execute_query(f"""
                UPDATE QUILLIAM.STG.MEETINGS
                SET STATUS = 'COMPLETED', ENDED_AT = CURRENT_TIMESTAMP()
                WHERE MEETING_ID = '{meeting_id}'
            """)
            return True
        except Exception as e:
            print(f"close_meeting failed for {meeting_id}: {str(e)}")
            return False

    async def _transcribe_archive_with_speakers(self, meeting_id: str) -> None:
        """Run speaker-level transcription on the archive file (chunk 0) using timestamp_granularity=speaker."""
        try:
            # Archive filename pattern: {meeting_id}_0_{date}_.mp3
            # Segments are: {meeting_id}_{chunk:03d}_{date}_.mp3 (3-digit chunk numbers)
            # Use RLIKE to match _0_ followed by a year (not _001_, _002_, etc.)
            files = await self.execute_query(f"""
                SELECT DISTINCT METADATA$FILENAME
                FROM @QUILLIAM.STG.AUDIO
                WHERE METADATA$FILENAME RLIKE '{meeting_id}_0_[0-9]{{4}}.*'
                LIMIT 1
            """)

            if not files:
                print(f"No archive file found on stage for meeting {meeting_id}")
                return

            archive_filename = files[0][0]

            transcription_sql = f"""
            INSERT INTO QUILLIAM.STG.MEETING_TRANSCRIPTS
                (MEETING_ID, CHUNK_NUMBER, TRANSCRIPT_TEXT, AUDIO_DURATION, CREATED_AT)
            WITH t AS (
                SELECT AI_TRANSCRIBE(
                    TO_FILE('@QUILLIAM.STG.AUDIO', '{archive_filename}'),
                    {{'timestamp_granularity': 'speaker'}}
                ) AS transcription
            )
            SELECT
                '{meeting_id}'                           AS MEETING_ID,
                0                                        AS CHUNK_NUMBER,
                transcription:text::TEXT                 AS TRANSCRIPT_TEXT,
                transcription:audio_duration::FLOAT      AS AUDIO_DURATION,
                CURRENT_TIMESTAMP()                      AS CREATED_AT
            FROM t
            WHERE transcription:text::TEXT IS NOT NULL
            """

            await self.execute_query(transcription_sql)
            print(f"Speaker-level archive transcription completed for meeting {meeting_id}")
        except Exception as e:
            print(f"Archive speaker transcription failed for {meeting_id}: {str(e)}")

    async def _generate_summary(self, meeting_id: str) -> None:
        """Use ai_complete() to generate a narrative meeting summary from the archive transcript (chunk 0)."""
        try:
            summary_sql = f"""
            UPDATE QUILLIAM.STG.MEETINGS
            SET SUMMARY = (
                WITH transcript AS (
                    SELECT TRANSCRIPT_TEXT AS full_text
                    FROM QUILLIAM.STG.MEETING_TRANSCRIPTS
                    WHERE MEETING_ID = '{meeting_id}'
                      AND CHUNK_NUMBER = 0
                      AND AUDIO_DURATION > 15
                    ORDER BY CREATED_AT DESC
                    LIMIT 1
                )
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    'llama3.1-70b',
                    CONCAT(
                        'You are a meeting assistant. Given the following meeting transcript, produce a structured summary with these sections:\\n',
                        '1. **Overview** - 2-3 sentence description of what was discussed and how the meeting flowed\\n',
                        '2. **Key Decisions** - bullet list of conclusions or agreements reached\\n',
                        '3. **Action Items** - bullet list with owner and task\\n',
                        '4. **Next Steps** - what needs to happen after this meeting\\n\\n',
                        'Transcript:\\n',
                        full_text
                    )
                )
                FROM transcript
                WHERE full_text IS NOT NULL AND LENGTH(full_text) > 20
            )
            WHERE MEETING_ID = '{meeting_id}'
            """
            await self.execute_query(summary_sql)
            print(f"Summary generated for meeting {meeting_id}")
        except Exception as e:
            print(f"Summary generation failed for {meeting_id}: {str(e)}")

    async def create_meeting(self, meeting_id: str) -> bool:
        """Insert a new meeting row when recording starts."""
        try:
            await self.execute_query(f"""
                INSERT INTO QUILLIAM.STG.MEETINGS (MEETING_ID, STATUS, STARTED_AT)
                VALUES ('{meeting_id}', 'IN_PROGRESS', CURRENT_TIMESTAMP())
            """)
            return True
        except Exception as e:
            print(f"create_meeting failed for {meeting_id}: {str(e)}")
            return False

    # ------------------------------------------------------------------
    # Meeting list & update
    # ------------------------------------------------------------------

    async def list_meetings(self) -> List[Dict[str, Any]]:
        """Return all meetings ordered by most recent."""
        try:
            results = await self.execute_query("""
                SELECT MEETING_ID, TITLE, STARTED_AT, ENDED_AT, STATUS, NOTES, SUMMARY
                FROM QUILLIAM.STG.MEETINGS
                ORDER BY STARTED_AT DESC
            """)
            return [
                {
                    'meeting_id': r[0],
                    'title': r[1],
                    'started_at': str(r[2]) if r[2] else None,
                    'ended_at': str(r[3]) if r[3] else None,
                    'status': r[4],
                    'notes': r[5],
                    'summary': r[6],
                }
                for r in results
            ]
        except Exception as e:
            print(f"list_meetings failed: {str(e)}")
            return []

    async def update_meeting(self, meeting_id: str, title: str = None, notes: str = None) -> bool:
        """Update meeting title and/or notes."""
        try:
            sets = []
            if title is not None:
                safe_title = title.replace("'", "''")
                sets.append(f"TITLE = '{safe_title}'")
            if notes is not None:
                safe_notes = notes.replace("'", "''")
                sets.append(f"NOTES = '{safe_notes}'")
            if not sets:
                return True
            await self.execute_query(f"""
                UPDATE QUILLIAM.STG.MEETINGS
                SET {', '.join(sets)}
                WHERE MEETING_ID = '{meeting_id}'
            """)
            return True
        except Exception as e:
            print(f"update_meeting failed for {meeting_id}: {str(e)}")
            return False

    # ------------------------------------------------------------------
    # Action Item CRUD
    # ------------------------------------------------------------------

    async def add_action_item(self, meeting_id: str, owner: str, task: str, due_date: str = None) -> Optional[int]:
        """Manually add an action item. Returns the new ID."""
        try:
            safe_task = task.replace("'", "''")
            safe_owner = (owner or '').replace("'", "''")
            safe_due = (due_date or '').replace("'", "''")
            await self.execute_query(f"""
                INSERT INTO QUILLIAM.STG.ACTION_ITEMS (MEETING_ID, OWNER, TASK, DUE_DATE, STATUS, CREATED_AT)
                VALUES ('{meeting_id}', '{safe_owner}', '{safe_task}', NULLIF('{safe_due}',''), 'OPEN', CURRENT_TIMESTAMP())
            """)
            result = await self.execute_query("SELECT MAX(ID) FROM QUILLIAM.STG.ACTION_ITEMS")
            return result[0][0] if result else None
        except Exception as e:
            print(f"add_action_item failed: {str(e)}")
            return None

    async def update_action_item(self, item_id: int, owner: str = None, task: str = None, due_date: str = None, status: str = None) -> bool:
        """Update an existing action item."""
        try:
            sets = []
            if owner is not None:
                sets.append(f"OWNER = '{owner.replace(chr(39), chr(39)+chr(39))}'")
            if task is not None:
                sets.append(f"TASK = '{task.replace(chr(39), chr(39)+chr(39))}'")
            if due_date is not None:
                sets.append(f"DUE_DATE = NULLIF('{due_date.replace(chr(39), chr(39)+chr(39))}','')")
            if status is not None:
                sets.append(f"STATUS = '{status}'")
            if not sets:
                return True
            await self.execute_query(f"UPDATE QUILLIAM.STG.ACTION_ITEMS SET {', '.join(sets)} WHERE ID = {item_id}")
            return True
        except Exception as e:
            print(f"update_action_item failed for {item_id}: {str(e)}")
            return False

    async def delete_action_item(self, item_id: int) -> bool:
        """Delete an action item."""
        try:
            await self.execute_query(f"DELETE FROM QUILLIAM.STG.ACTION_ITEMS WHERE ID = {item_id}")
            return True
        except Exception as e:
            print(f"delete_action_item failed for {item_id}: {str(e)}")
            return False

    # ------------------------------------------------------------------
    # Decision CRUD
    # ------------------------------------------------------------------

    async def add_decision(self, meeting_id: str, text: str) -> Optional[int]:
        """Manually add a decision. Returns the new ID."""
        try:
            safe_text = text.replace("'", "''")
            await self.execute_query(f"""
                INSERT INTO QUILLIAM.STG.DECISIONS (MEETING_ID, DECISION_TEXT, CREATED_AT)
                VALUES ('{meeting_id}', '{safe_text}', CURRENT_TIMESTAMP())
            """)
            result = await self.execute_query("SELECT MAX(ID) FROM QUILLIAM.STG.DECISIONS")
            return result[0][0] if result else None
        except Exception as e:
            print(f"add_decision failed: {str(e)}")
            return None

    async def update_decision(self, decision_id: int, text: str) -> bool:
        """Update a decision's text."""
        try:
            safe_text = text.replace("'", "''")
            await self.execute_query(f"UPDATE QUILLIAM.STG.DECISIONS SET DECISION_TEXT = '{safe_text}' WHERE ID = {decision_id}")
            return True
        except Exception as e:
            print(f"update_decision failed for {decision_id}: {str(e)}")
            return False

    async def delete_decision(self, decision_id: int) -> bool:
        """Delete a decision."""
        try:
            await self.execute_query(f"DELETE FROM QUILLIAM.STG.DECISIONS WHERE ID = {decision_id}")
            return True
        except Exception as e:
            print(f"delete_decision failed for {decision_id}: {str(e)}")
            return False

    # ------------------------------------------------------------------
    # Agent chat via REST API
    # ------------------------------------------------------------------

    async def run_agent(self, message: str, meeting_id: str = None) -> str:
        """Call the Quilliam agent via the Snowflake REST API (non-streaming)."""
        try:
            # Build the message with optional meeting context
            user_text = message
            if meeting_id:
                user_text = f"[Context: The user is asking about meeting {meeting_id}. Focus your search and queries on this specific meeting.]\n\n{message}"

            # Get auth token from the active connection
            token = self.connection.rest.token
            account = self.config['account']

            # Build Snowflake REST URL
            # Account format: ORG-ACCOUNT -> org-account.snowflakecomputing.com
            host = account.replace('_', '-').lower() + '.snowflakecomputing.com'
            url = f"https://{host}/api/v2/databases/QUILLIAM/schemas/STG/agents/QUILLIAM_AGENT:run"

            headers = {
                'Authorization': f'Snowflake Token="{token}"',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }

            payload = {
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": user_text}]
                    }
                ]
            }

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=payload, headers=headers, timeout=120)
            )

            if response.status_code != 200:
                print(f"Agent API error {response.status_code}: {response.text[:500]}")
                return f"Error: Agent returned status {response.status_code}"

            data = response.json()

            # Extract text content from the response
            text_parts = []
            for item in data.get('content', []):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))

            return '\n'.join(text_parts) if text_parts else "The agent did not return a text response."

        except Exception as e:
            print(f"run_agent failed: {str(e)}")
            return f"Error: {str(e)}"
