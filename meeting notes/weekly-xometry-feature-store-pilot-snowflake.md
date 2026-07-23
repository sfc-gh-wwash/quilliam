This weekly check-in focused on standing up the Xometry feature store pilot, validating the first benchmark baseline, and tightening the weekly execution plan.

### Overall Summary
The team reviewed the setup materials for Snowflake’s online feature store, including documentation and a step-by-step notebook, and aligned on using Xometry’s current production metrics as the baseline for comparison. The main unresolved item is how to move or expose Xometry’s existing model data so it can be used by the online feature store in the pilot environment.

### Meeting Flow
- **William** opened by sending two resources: the online feature store documentation and a notebook that walks through setup step by step. He noted the notebook should help the team get the environment working in Snowflake, but it will need to be adjusted to match Xometry’s setup.
- The discussion then moved to data movement and architecture. The Xometry team said the relevant data already exists in Snowflake and asked whether the feature store can query it directly from there or whether it must be ingested from the data lake into the online store. **William** said he needs to go back to product to confirm the best path, including whether there is an easy way to bulk load data into Postgres for the online feature store.
- The group shifted to benchmarking. The Xometry team raised the need for current performance benchmarks and SLAs so the pilot can be measured against what exists today. Instead of waiting on email, they shared a live dashboard showing route-level P95 latency and traffic. They highlighted that traffic is close to two million requests per day, with about one million during working hours, and pointed to the slowest, highest-traffic route as the most important candidate because improving it would have outsized product impact. A latency figure of about 649 ms was called out for that route.
- In the final part of the meeting, the team discussed project tracking and cadence. A project plan is nearly ready, and the stated target is to have everything collected by **the end of September / end of Q3**. The group also corrected the recurring meeting schedule: this working session should happen weekly, not every 10 weeks.

### Decisions Made
- The team will use the currently shared dashboard metrics as the initial benchmark baseline — agreed by **William** and the Xometry team.
- The working session cadence is weekly — agreed by **William** and the team.

### Action Items
- **William**: Ask product and the added stakeholders about the best way to load Xometry data into the online feature store environment, including whether bulk loading into Postgres is required — Due: **TBD**
- **Xometry team**: Confirm which route is the pilot focus if the highlighted slowest/highest-traffic route is not already the intended one — Due: **TBD**
- **Jamie**: Update the project plan / recurring schedule to reflect a weekly cadence and share the plan with participants as needed — Due: **TBD**
- **Xometry team**: Work through the setup notebook this week and bring follow-up questions to the next meeting — Due: **next week**

### Open Questions
- Can the pilot use data already stored in Snowflake directly, or must that data be loaded separately into the online feature store path?
- Is the highlighted “win rate” route definitively the endpoint the pilot will optimize, or does that still need confirmation?