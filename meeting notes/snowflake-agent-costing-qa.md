This meeting focused on technical questions from a team building agents on Snowflake, with emphasis on token usage, cost control, observability, and product gaps. The main outcome was that several issues could not be resolved live, so **William Wash** committed to investigate telemetry, take gaps back to product and engineering, and coordinate a follow-up with specialists.

### Overall Summary
The customer team said they are committed to building on Snowflake and wanted expert guidance on how agent behavior affects token consumption, cost, and admin controls. The most important takeaway was that there appear to be inconsistencies between configured token limits, observed token usage, and reporting views, and those need deeper follow-up rather than an immediate answer.

### Meeting Flow
- The team opened by explaining that they are building agents on Snowflake and generally like the platform, but wanted to review technical questions that had come up during implementation, especially around cost and behavior.
- The first major topic was a token-limit discrepancy: when the same question was asked through Claude Desktop connected to the MCP server, the request hit the configured limit and stopped, but when asked through the Snowflake-hosted agent experience, it still consumed roughly 68,000 tokens in observability. **William Wash** said that behavior did not sound correct and he would review telemetry and take it back to product.
- The team then asked whether they could force a default model such as Sonnet 5.6. **William Wash** said that is not currently supported; the system uses automatic model selection today, but the ability to constrain or pin model choice is on the roadmap.
- Another discussion focused on responses that include the full semantic view when the agent is called directly. The team said this increases token burn in external LLM flows and may worsen hallucinations. **William Wash** said the semantic view is part of the prompt sent to generate SQL, but agreed that an option to suppress or trim it sounded like a product gap worth raising.
- The group then dug into AI cost tracking and reporting. They reviewed built-in usage tables, API usage history, AI SQL usage history, and the observability portal, and noted discrepancies between token counts across sources for the same request. **William Wash** said total AI services cost can be derived from metering history and rate sheet data, but that different surfaces may be needed to capture all usage paths.
- Finally, the team asked about an orchestration layer that could route questions across multiple agents, plus separate monitoring and control for Cortex Search costs. **William Wash** said the “agent of agents” concept is on the roadmap and that he would email follow-up guidance on Cortex Search controls and scheduling with specialists.

### Action Items
- **William Wash**: Investigate why the Snowflake-hosted agent path appears not to honor configured token limits and review telemetry from the examples shown on the call — Due: **TBD**
- **Aditya**: Send **William Wash** the relevant query, DDL, and supporting screenshots/request details for the token and observability discrepancy investigation — Due: **TBD**
- **William Wash**: Raise product follow-ups on semantic-view trimming, model-default controls, and agent orchestration; engage specialists and send follow-up meeting times by email — Due: **TBD**
- **William Wash**: Email guidance on how to monitor or control Cortex Search costs separately — Due: **TBD**

### Open Questions
- Why does the Snowflake-hosted agent experience appear to ignore configured token limits when Claude Desktop plus MCP does not?
- Why do token counts differ between the observability portal and built-in request or usage tables for the same request?
- Will admins get finer controls for default model selection, semantic-view suppression, multi-agent orchestration, and Cortex Search cost governance?