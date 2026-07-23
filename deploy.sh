#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$PROJECT_DIR/database"
APP_VERSION=$(cat "$PROJECT_DIR/VERSION" | tr -d '[:space:]')

echo "Deploying Quilliam v${APP_VERSION} to Snowflake..."
echo ""

# Check for snow CLI
if command -v snow &> /dev/null; then
    SNOW_CMD="snow"
else
    echo "Error: 'snow' (Snowflake CLI) not found."
    echo "Install: pip install snowflake-cli"
    exit 1
fi

run_sql_file() {
    local file=$1
    local desc=$2
    echo "  [$desc] Running $(basename "$file")..."
    snow sql -f "$file" --role ACCOUNTADMIN 2>&1 | tail -1
}

run_sql() {
    snow sql -q "$1" --role QUILLIAM_ADMIN_RL 2>&1 | tail -1
}

# Check current deployed version
echo "Checking deployed version..."
DEPLOYED_VERSION=$(snow sql -q "SELECT MAX(VERSION) FROM QUILLIAM.STG.APP_VERSION" --role ACCOUNTADMIN 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "0.0")

if [ "$DEPLOYED_VERSION" = "$APP_VERSION" ]; then
    echo "Already at v${APP_VERSION}. No deployment needed."
    echo "Use --force to redeploy anyway."
    if [ "$1" != "--force" ]; then
        exit 0
    fi
    echo "  --force specified, redeploying..."
fi

echo "  Deployed: v${DEPLOYED_VERSION:-none} → v${APP_VERSION}"
echo ""

# Deploy in order
echo "Step 1/5: Base DDL (database, schema, stage, tables)"
run_sql_file "$DB_DIR/meeting_notes_ddl.sql" "DDL"

echo "Step 2/5: Cortex Search Services"
run_sql_file "$DB_DIR/cortex_search_service.sql" "Search"

echo "Step 3/5: Semantic View"
run_sql_file "$DB_DIR/semantic_view.sql" "Semantic View"

echo "Step 4/5: Cortex Agent"
run_sql_file "$DB_DIR/cortex_agent.sql" "Agent"

echo "Step 5/5: MCP Connectors"
run_sql_file "$DB_DIR/mcp_connectors.sql" "MCP"

# Stamp version
echo ""
echo "Stamping version ${APP_VERSION}..."
snow sql -q "INSERT INTO QUILLIAM.STG.APP_VERSION (VERSION) VALUES ('${APP_VERSION}')" --role ACCOUNTADMIN 2>/dev/null

echo ""
echo "Deployment complete! (v${APP_VERSION})"
echo ""
echo "Objects:"
echo "  Database:         QUILLIAM.STG"
echo "  Stage:            @QUILLIAM.STG.AUDIO"
echo "  Search Services:  MEETING_TRANSCRIPT_SEARCH, MEETING_NOTES_SEARCH, MEETING_SUMMARY_SEARCH"
echo "  Semantic View:    MEETING_ANALYTICS_SV"
echo "  Agent:            QUILLIAM_AGENT"
echo "  MCP Servers:      GMAIL_MCP, GOOGLE_CALENDAR_MCP, SLACK_MCP"
echo "  User/Role:        QUILLIAM_ADMIN / QUILLIAM_ADMIN_RL"
echo "  Warehouse:        QUILLIAM_WH"
echo ""
echo "Next steps:"
echo "  1. Set RSA public key: ALTER USER QUILLIAM_ADMIN SET RSA_PUBLIC_KEY='...';"
echo "  2. Copy private key to backend/rsa_key.p8"
echo "  3. Run ./start.sh to launch the app"
