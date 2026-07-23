Xometry and Snowflake used this session to narrow the roadmap conversation to the highest-impact areas where Snowflake input is needed, especially around migration feasibility, performance expectations, and architecture alignment. The clearest outcome was agreement to prioritize evidence-gathering for the Feature Store and ClickHouse migration paths over the next several weeks so Xometry can make recommendations in Q3 and, if warranted, move in Q4.

### Overall Summary

The discussion focused on how Snowflake can support Xometry’s global data platform roadmap without overreaching into adjacent BI-tool ownership. Most of the meeting centered on validating SLA expectations, clarifying the difference between Snowflake Feature Store/Postgres and Interactive Warehouses, and defining the next steps for benchmarking and architecture review.

### Meeting Flow

- The group aligned on process: Xometry had received SLA benchmarks from Gabrielle and Carlos, planned to review them with product leaders early the following week, and asked Snowflake to help stack-rank where strategic input was most needed.
- They reviewed performance-sensitive workloads, especially the most-used route, customer profiles, and other high-request paths. Xometry emphasized that any slowdown in production-facing services would affect the website, so migration decisions need measured evidence rather than rough estimates.
- A substantial portion of the meeting clarified architecture options for replacing ClickHouse. William explained that Snowflake Feature Store runs on managed Postgres, while Interactive Warehouses are a separate Snowflake capability better suited to read-heavy, low-latency, high-concurrency workloads. Liz clarified that her immediate need was confidence on query speed and whether existing ClickHouse tables could simply be mirrored into Snowflake/Postgres.
- The team discussed broader roadmap boundaries. Snowflake offered customer introductions for BI tools such as Sigma, Omni, and Hex, but Xometry drew a line that BI tool ownership sits with other teams; their focus remains data/infrastructure, analytics engineering input, and ML/AI-related workstreams.
- They also covered adjacent roadmap items: an ingestion-to-BI proof of concept using Snowflake-managed Iceberg tables, ML platform standardization across regions, database consolidation/cleanup, and possible future interest in Snowflake agent orchestration and automation capabilities.
- The meeting closed on commercial and executive-planning topics. Xometry noted rising Snowflake consumption driven by broader adoption, Cortex usage, and new data applications, while also facing pressure to reduce operational spend. Both sides agreed to pair technical roadmap work with financial planning and executive narrative development.

### Decisions Made

- [Decision] Prioritize the Feature Store migration POC and ClickHouse migration benchmarking as the main near-term focus — agreed by Xometry and Snowflake.
- [Decision] BI tooling selection and analytics workstreams will remain outside this team’s direct ownership — agreed by Xometry.

### Action Items

- **Xometry product team**: Review SLA benchmarks from Gabrielle and Carlos and incorporate conclusions into the project plan — Due: **early next week**
- **William**: Send Liz a Slack message outlining the table metadata, DDL, sizes, and example-query details needed for benchmarking — Due: **today**
- **Liz**: Provide the requested ClickHouse table details and example queries to support Snowflake testing — Due: **TBD**
- **Snowflake team**: Return with a topical update after meeting with product leaders on SLA outcomes — Due: **end of next week**
- **Snowflake team**: Gather evidence for the Feature Store and ClickHouse migration POCs — Due: **over the next 45 days**
- **Snowflake team**: Draft the ask and framing for a possible executive engagement/CEC-style session — Due: **TBD**

### Open Questions

- Whether ClickHouse replacement should use Snowflake/Postgres mirroring, Interactive Warehouses, or a different target-state design
- What performance delta is acceptable for production-facing workloads
- How Xometry should balance expanding Snowflake usage with tighter cost controls and future planning