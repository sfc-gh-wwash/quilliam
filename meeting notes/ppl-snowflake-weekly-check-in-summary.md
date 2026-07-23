The team aligned on a directionally accurate approach for Snowflake sizing tied to PPL’s SAP and adjacent data workloads. The main outcome was agreement on simpler, defensible assumptions for year-one sizing now, with a few follow-ups needed to fill in “other data products” and finalize the contract extension estimate.

### Overall Summary
The discussion focused on refining a spreadsheet used to size Snowflake for PPL’s upcoming SAP-related workloads and broader data platform growth. The group agreed to use lighter, high-level assumptions rather than waiting for perfect detail, especially around SAP data volume, reporting growth, and how year-one replication may later shift toward zero-copy patterns.

### Meeting Flow
- The team began by reviewing the working spreadsheet and agreeing that it did not need to be complete to be useful; directionally accurate inputs were enough to support sizing.
- They then worked through SAP scope and data-volume assumptions. The group noted that SAP source sizing figures likely represent multi-year capacity, not just immediate needs, and aligned on using a smaller subset of total transactional data for Snowflake planning, with daily ingestion as the default cadence and relatively light transformation workload.
- The conversation shifted to architecture. The team clarified that year one may require physically replicating SAP-derived data into Snowflake and Databricks, while future-state access could rely more on SAP Business Data Cloud and zero-copy patterns. They also distinguished this from non-SAP historical data that may be exposed via Iceberg/open formats.
- Next, they revisited a spreadsheet section labeled “dynamic data mart.” The group concluded that label was misleading and that the section should instead capture “other data products” or other aggregate non-SAP data sources, without forcing a source-by-source inventory.
- The final part of the meeting covered reporting and contract timing. The team agreed that data growth will be steeper than report growth because PPL wants more self-service and fewer new fixed reports. They also discussed the upcoming Snowflake extension and the need for a sizing-based order form quickly enough to support internal supply-chain review.

### Decisions Made
- [Decision] Use a lighter SAP sizing assumption at a high level, roughly **20%** of available SAP data rather than larger day-one percentages — agreed by **William**, **Govind**, and the PPL team.
- [Decision] Replace the “dynamic data mart” concept with an “other data products” aggregate estimate — agreed by **William** and the PPL team.
- [Decision] Use **10%** report growth for planning instead of **20%** — agreed by the group.

### Action Items
- **Prasenjit**: Update the spreadsheet with the revised SAP assumptions and rename/add the “other data products” section with aggregate volume and pipeline estimates — Due: TBD
- **William**: Use the current inputs to prepare Snowflake sizing guidance and get the order form/estimate over to the PPL team — Due: **tomorrow** or **Monday**
- **Govind**: Take the sizing/order-form output to supply chain for extension review — Due: TBD

### Open Questions
- What additional non-SAP “other data products” should be included in the aggregate estimate for next year?
- Will the contract extension be structured as a **one-year** O&amp;M renewal or a longer term if capital treatment becomes possible?
- How much SAP data will still need physical replication after year one once Business Data Cloud is available?