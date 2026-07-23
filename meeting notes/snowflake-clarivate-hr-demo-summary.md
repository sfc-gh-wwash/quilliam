This meeting focused on a Snowflake demo for Clarivate’s HR use case, centered on Workday zero-copy integration, governance, natural-language access to HR data, and rapid app/report prototyping. The main outcome was a shared understanding of how Snowflake could reduce manual Workday report exports and enable governed self-service analytics, while Clarivate identified follow-up questions on Workday-side cost and operating model.

### Overall Summary
Snowflake walked through an end-to-end vision: ingest Workday data through zero-copy integration, model it with dynamic tables and semantic views, expose it through governed agents, and optionally turn analyses into Streamlit apps or scheduled reports. Clarivate’s team was interested, but wants to validate cost, governance boundaries, and how responsibilities should be split with their IT/data teams before moving forward.

### Meeting Flow
- William recapped the prior conversation and framed the demo around three themes: Workday zero-copy integration, handling HR history changes such as rehires and hierarchy updates, and using natural language plus agentic coding to work with the data.
- The group discussed current-state friction: Clarivate exports Workday reports manually for Adam’s team to ingest. William explained the private-preview Workday zero-copy approach, where Workday tables would appear in Snowflake without a separate ETL pipeline, and noted Snowflake would not charge storage or ingestion fees for that pattern.
- The discussion shifted to governance. William recommended building views on top of provider-managed tables to protect downstream reports from schema changes, then applying Snowflake controls such as masking, projection policies, aggregation policies, and row-level security to protect sensitive HR data like salary.
- William showed how dynamic tables could maintain derived HR datasets such as headcount snapshots and support slowly changing dimension patterns to preserve historical attribute changes over time.
- The demo then moved into Cortex Code and CoCo, showing how builders can use natural language to modify SQL objects, apply governance policies, connect MCP tools like Jira, Glean, Gmail, Salesforce, and Workday, and prototype pipelines or apps without hand-writing all code.
- William demonstrated Cortex Analyst, semantic views, verified queries, skills, and agents as the governed business-user experience. He emphasized routing HR questions to curated tools, adding “truth-seeking” counter-evidence, limiting agents to aggregate-only responses when needed, and using evaluation datasets plus user feedback to monitor quality.
- The meeting closed with Streamlit as a prototyping path for dashboards and recurring reports. Clarivate said the demo was helpful but needs time to digest it, and wants input from Adam’s and Brian’s teams on feasibility, management model, and next steps.

### Action Items
- **Clarivate team**: Get input from **Adam’s** team and **Brian’s** team on governance, ownership, and what is feasible between the teams — Due: **TBD**
- **Snowflake / William**: Follow up with **Brian** and team to share what was shown and continue next-step discussions — Due: **TBD**
- **Clarivate team**: Confirm Workday-side cost and commercial implications of the zero-copy integration — Due: **TBD**
- **Snowflake and Clarivate**: Run a sizing exercise with **Brian**, **Adam**, and related team members to estimate operating cost more precisely — Due: **TBD**

### Open Questions
- What, if anything, would Workday charge for the zero-copy integration?
- Should Clarivate centralize these capabilities through IT/data teams, or allow more self-service prototyping by business or builder personas?
- For any Workday MCP integration, should access be read-only to prevent unintended updates?
- How should prototype Streamlit outputs transition into production reporting tools such as Power BI or Sigma?