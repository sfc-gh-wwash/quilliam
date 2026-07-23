The team aligned on how to help iPipeline and **Seth Roy** identify a fast, sellable data product despite internal delivery bottlenecks.

### Overall Summary
The discussion focused on creating a practical plan for iPipeline to launch a new data product quickly, rather than waiting on slow internal migrations and architecture work. The most important outcome was alignment on two candidate paths to take back to **Seth Roy**, with a preference for a higher-value InsureSight-style offering packaged with semantic modeling and an agentic “talk to your data” experience.

### Meeting Flow
- The group framed **Seth Roy’s** challenge: he needs new SKUs he can sell, but his product team depends on an internal data team that is moving too slowly. Legal work around a separate scoring initiative is progressing, but not fast enough to solve his immediate need for something new to bring to market.
- Two opportunity paths emerged. The first was a cost-focused play: help iPipeline reduce pressure around Sigma by putting a strong semantic model and chat-style interface on top of existing reporting so they can either lower front-end cost or improve negotiating leverage.
- The second, and more compelling, path was a net-new InsureSight-style product built around data iPipeline has that carriers do not: aggregated early-funnel agent and market activity. The team discussed anonymized benchmarking, market trend analysis, and a package that combines curated data, semantic views, dashboards, and natural-language querying.
- The team then pressure-tested feasibility. Data fragmentation and the unfinished iGO / AMS migrations into an Iceberg-centric model are still blockers, but the group felt a narrower single-domain use case—likely centered on iGO—could be built from data already in Snowflake instead of waiting on “never-ending architecture work.”
- Conversation shifted to execution risk. Several participants said iPipeline’s combined data engineering and analytics team remains the recurring bottleneck, is resistant to outside help from Hakoda, and has also rejected using CoCo. The group agreed that showing a tangible MVP quickly is more likely to change minds than continuing to debate capabilities abstractly.
- They closed on a go-forward motion: talk **Seth Roy** through both paths, keep scope tight, steer Hakoda toward a proposal Snowflake believes can succeed quickly, and use a funded hackathon to produce something concrete.

### Decisions Made
- [Decision] Present **Seth Roy** with two parallel paths: a Sigma cost/semantic-model option and a net-new InsureSight-style data product option — agreed by **William**, **Rob**, and the group.
- [Decision] Keep the initial build conversation scoped to Snowflake, Hakoda, and **Seth Roy’s** team to avoid early pushback from iPipeline’s data engineering team — agreed by the group.
- [Decision] Use the funded Hakoda half-day hackathon to target an MVP rather than a fully baked product — agreed by the group.

### Action Items
- **William**: Reach out to **Seth Roy** and get time on the calendar for an hour-long discussion, potentially with one or two of his directs — Due: **ASAP**
- **William**: Coordinate logistics and schedule the follow-up session around **Sully McConnell’s** availability — Due: **next 1–2 weeks**
- **William** and **team**: Use the **3:00 today** partner meeting to steer Hakoda toward a unified plan before taking it back to **Seth Roy** — Due: **3:00 today**

### Open Questions
- Can the team build enough value on current Snowflake-resident data without waiting for broader iGO and AMS migrations?
- Will **Seth Roy** be able to secure either internal resources or approval for Hakoda to build?
- Can iPipeline be convinced to enable and adopt CoCo as part of the acceleration approach?