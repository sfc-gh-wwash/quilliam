#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$PROJECT_DIR/database"

echo "Deploying Quilliam to Snowflake..."
echo ""

# Check for SnowSQL or snow CLI
if command -v snow &> /dev/null; then
    SNOW_CMD="snow sql -q"
elif command -v snowsql &> /dev/null; then
    SNOW_CMD="snowsql -q"
else
    echo "Error: Neither 'snow' (Snowflake CLI) nor 'snowsql' found."
    echo "Install one of:"
    echo "  pip install snowflake-cli"
    echo "  https://docs.snowflake.com/en/user-guide/snowsql"
    exit 1
fi

run_sql_file() {
    local file=$1
    local desc=$2
    echo "[$desc] Running $file..."
    if command -v snow &> /dev/null; then
        snow sql -f "$file" --role ACCOUNTADMIN
    else
        snowsql -f "$file" -r ACCOUNTADMIN
    fi
    echo "  Done."
    echo ""
}

# Deploy in order
echo "Step 1/4: Base DDL (database, schema, stage, tables, user, role, warehouse)"
run_sql_file "$DB_DIR/meeting_notes_ddl.sql" "DDL"

echo "Step 2/4: Cortex Search Service"
run_sql_file "$DB_DIR/cortex_search_service.sql" "Search"

echo "Step 3/4: Semantic View"
run_sql_file "$DB_DIR/semantic_view.sql" "Semantic View"

echo "Step 4/4: Cortex Agent"
run_sql_file "$DB_DIR/cortex_agent.sql" "Agent"

echo ""
echo "Deployment complete!"
echo ""
echo "Objects created:"
echo "  Database:       QUILLIAM.STG"
echo "  Stage:          @QUILLIAM.STG.AUDIO"
echo "  Search Service: QUILLIAM.STG.MEETING_TRANSCRIPT_SEARCH"
echo "  Semantic View:  QUILLIAM.STG.MEETING_ANALYTICS_SV"
echo "  Agent:          QUILLIAM.STG.QUILLIAM_AGENT"
echo "  User:           QUILLIAM_ADMIN"
echo "  Role:           QUILLIAM_ADMIN_RL"
echo "  Warehouse:      QUILLIAM_WH"
echo ""
echo "Next steps:"
echo "  1. Set RSA public key: ALTER USER QUILLIAM_ADMIN SET RSA_PUBLIC_KEY='...';"
echo "  2. Copy private key to backend/rsa_key.p8"
echo "  3. Run ./start.sh to launch the app"
