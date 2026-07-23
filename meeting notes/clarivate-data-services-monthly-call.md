This call focused on Clarivate Data Services delivery status, current Snowflake-related work, and near-term risks tied to both platform changes and business events. The most important outcome was that the dynamic table defect blocking final validation now appears to have a fix, which should let the NetSuite work resume and move toward BI handoff.

### Overall Summary
Clarivate shared mostly positive project updates, with the main concern being time-sensitive execution rather than overall direction. The team is balancing a hard Q1 deadline to migrate from NetSuite 1 to NetSuite 2, active adoption of DCM Projects, ongoing work with Hakoda, and uncertainty around the LSH divestiture’s eventual contract impact.

### Meeting Flow
- The group opened with a brief discussion of the recent buyer announcement and divestiture context. Everyone agreed it is still too early to assess the outcome, details remain restricted, and the practical impact on the contract is still largely unknown.
- Clarivate then reviewed the biggest operational risk: moving NetSuite data into Snowflake. NetSuite’s API performance, lack of primary keys on large tables, and timeout issues have slowed full-load ingestion, while Oracle’s end-of-Q1 shutdown of NetSuite 1 creates a fixed deadline to migrate data, rebuild reports on NetSuite 2, and transition users.
- The team discussed the dynamic table refresh defect that had paused final data model validation. Clarivate reported that a fix was finally delivered, and Snowflake clarified that future production-blocking or deadline-sensitive issues should be escalated directly rather than allowed to sit in normal ticket flow.
- Clarivate shared that DCM Projects adoption has gone well. They have stopped manually promoting most code across environments, now use DCM Projects for infrastructure builds, and only keep security grants and role provisioning outside that workflow.
- The final part of the call covered forward-looking work: lessons from Summit on adaptive warehouses, progress with Hakoda’s current-state and migration POC work, and a kickoff to bring the IP Sales Snowflake footprint into the Data Services account with stronger governance and more standardized operating practices.

### Decisions Made
- [Decision] Critical, showstopping issues tied to production delivery or hard deadlines should be escalated directly to **Ed** and the Snowflake team rather than handled only through standard support updates.
- [Decision] Clarivate will continue using DCM Projects as the default path for code promotion and most infrastructure deployment; security grants and role provisioning remain manual.

### Action Items
- **Clarivate team**: Test the dynamic table defect fix and, if successful, complete final data model validation and hand off to the BI team — Due: **TBD**
- **Clarivate team**: Send **Ed** and **William** the Summit follow-up on adaptive warehouses/public preview details — Due: **TBD**
- **Snowflake team**: Review the defect fix outcome and advise on adaptive warehouse timing and alternatives such as query acceleration service — Due: **TBD**
- **Clarivate IP team**: Kick off migration planning to move IP Sales workloads into the Data Services Snowflake account — Due: **tomorrow**

### Open Questions
- What effect will the LSH divestiture have on the Clarivate contract after year-end?
- Will adaptive warehouses provide enough cost or performance benefit to justify adoption versus other options?
- Can the NetSuite 2 migration complete cleanly before the Oracle-imposed Q1 cutoff?