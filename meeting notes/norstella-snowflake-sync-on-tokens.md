The meeting focused on validating Norstella’s Snowflake AI cost-estimation approach and agreeing on next steps to improve cost visibility before broader internal rollout. The most important outcome was alignment that the current custom query likely needs refinement to avoid double counting, and that **Paul** will send an updated query with more accurate cost granularity.

### Overall Summary
Norstella asked Snowflake to review an internally built cost query because leadership is becoming concerned about Snowflake AI spend and wants better forecasting before usage scales further. The discussion covered where duplicate usage may appear across account usage views, how token-based AI pricing works, where warehouse costs still apply, and broader concerns about governance, security, and “shadow BI” as teams experiment with AI-generated dashboards.

### Meeting Flow
* The conversation opened with urgency from the Norstella side: they had shown leadership early Snowflake cost estimates and wanted to confirm whether the current query was accurate enough to use for forecasting and budget monitoring.
* They reviewed the engineer’s view built from multiple Snowflake account usage objects. Snowflake noted that some joins may create duplicate counting, especially because usage that appears in `CORTEX_AGENT_USAGE_HISTORY` can also surface in `SNOWFLAKE_INTELLIGENCE_USAGE_HISTORY`, so the current approach needs validation.
* The group then walked through pricing mechanics. Snowflake explained that AI Credits are separate from standard Snowflake credits, priced at about $2 per AI credit, with model-specific rates for input and output tokens. They also clarified that AI SQL usage incurs both AI token charges and normal warehouse compute charges.
* Norstella showed a flatter cost table they had assembled and discussed handling input, output, and cached tokens. Snowflake confirmed cached reads and writes are billed differently and said a better Snowflake-recommended query would be more useful than continuing to tune the current estimate manually.
* The discussion broadened into operating concerns: current experimentation is intentionally open, but Norstella worries about runaway cost, insecure AI-generated dashboards, proliferation of conflicting BI outputs, and lack of a governed single source of truth. One example discussed was a Claude-generated dashboard pattern estimated at roughly $250,000 annually if replicated broadly.
* The meeting ended with agreement to share a better query, use Snowflake’s Admin > Cost Management views for near-term visibility, plan a broader leadership/QBR-style session, and explore whether routing future Anthropic usage through Snowflake could improve pricing at renewal time.

### Decisions Made
* [Decision] Norstella will use Snowflake’s built-in Cost Management and Consumption views as the immediate source for running spend visibility while the custom query is refined — agreed by the group.
* [Decision] The teams will set up a broader roadmap and leadership alignment session in a QBR-style format — agreed by both sides.

### Action Items
* **Paul**: Send Norstella an updated Snowflake query with more accurate cost logic and granularity — Due: **later today or tomorrow**
* **Paul**: Share the observability app / Git-based solution once ready so Norstella can inspect token usage, users, roles, tags, and requests more directly — Due: **this week or next week**
* **Norstella team**: Review Admin > Cost Management > Consumption and consider tagging resources by business unit, product, or agent for better internal reporting — Due: TBD
* **Both teams**: Schedule a leadership/QBR session to review roadmap, best practices, governance, and cost controls — Due: TBD

### Open Questions
* What is the best Snowflake-recommended query structure to avoid double counting across the various AI usage history views?
* What governance controls should Norstella implement to limit insecure or redundant AI-generated BI assets while keeping experimentation open?
* Can Norstella reduce future Anthropic costs by routing more usage through Snowflake during the next contract or renewal cycle?