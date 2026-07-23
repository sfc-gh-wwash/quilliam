This discussion focused on Atalia Horenshtien’s readout of Clarivate’s near-term Snowflake priorities and how Snowflake and Hakkoda should position follow-on work ahead of Clarivate’s next budget cycle. The clearest outcome was that Clarivate’s migration work is going well overall, funding for the core migration appears secure, and there is a timely opportunity to shape several adjacent use cases for next year.

### Overall Summary
Atalia shared five Clarivate use-case areas she developed from Summit conversations and follow-up discussions with Brian and Adam, with explicit priority and budget context. The group aligned that the top opportunities are the core migration off Redshift and Bouquet plus a secure client-facing data-sharing pattern, while automation, self-service analytics, and monetization remain important expansion areas that need further stakeholder engagement.

### Meeting Flow
- Atalia opened with a status update on the current assessment for migrating Clarivate from Redshift and Bouquet to Snowflake, noting the project is about a month behind because of Clarivate-side access delays, but overall feedback on the team and progress has been positive.
- She then framed five follow-on use cases to prepare ahead of Clarivate’s budget cycle in roughly six weeks, explaining that use cases 1 and 2 are top CIO priorities, use case 3 is a top priority for Brian’s team, use case 4 is more of a nice-to-have today, and use case 5 lacks enough detail because it sits with the product team.
- The first use case was the full migration program: de-risking with a possible dual run, adding Oracle as another source into Snowflake, and eventually addressing smaller “orphan” warehouses created through acquisitions and shadow IT. Atalia said this work is already CIO-approved and retirement of Bouquet should help secure funding.
- The second use case was designing a secure client-facing Snowflake pattern, with strong CIO interest in multi-tenant secure data sharing that separates client data exposure from internal house data. Atalia proposed running this in parallel with migration planning.
- The third use case centered on automation for testing, quality checks, and ingestion. The group discussed Clarivate’s heavy manual processes and the need for better ingestion patterns, guardrails, and AI-enabled automation as part of the broader medallion-style migration.
- The last part of the meeting covered business-facing analytics and monetization. The team agreed Clarivate may be underestimating the urgency of replacing legacy Power BI/reporting workflows with self-service or conversational analytics, while monetization needs discovery with product-side stakeholders such as Scott McCarthy. They also discussed proactively introducing Snowflake/Hakkoda to Clarivate business units to accelerate adoption once more data lands in Snowflake.

### Decisions Made
- [Decision] Run the secure client-facing architecture discussion in parallel with migration planning — agreed by Atalia and the Snowflake team.
- [Decision] Start exploring introductions into Clarivate lines of business now, rather than waiting for all data to land in Snowflake — agreed by the group.

### Action Items
- **Atalia Horenshtien**: Send the use-case deck to the Snowflake team — Due: **TBD**
- **Atalia Horenshtien**: Speak with **Santosh** next week to brief him on the Clarivate use cases and adjacent IBM opportunities — Due: **next week**
- **Adam**: Introduce the team to **Scott McCarthy** on the product side for monetization discovery — Due: **TBD**
- **Snowflake team**: Share any customer discussions or examples related to use case 4, moving from dashboards toward agents/self-service analytics — Due: **TBD**
- **Atalia Horenshtien**: Identify the right Clarivate line-of-business stakeholders for future introductions and workshops — Due: **TBD**

### Open Questions
- Who should own and sponsor the proposed “art of the possible” workshop for Clarivate business stakeholders?
- Which Clarivate business units should be approached first for self-service analytics and data access acceleration?
- What are **Scott McCarthy’s** priorities, pain points, and current monetization approach on the product side?