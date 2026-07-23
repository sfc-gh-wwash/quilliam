Here is your meeting summary.

### Overall Summary
The meeting focused on two linked topics: the unusually high Snowflake costs tied to PPL’s ongoing data repair work, and near-term renewal planning with Accenture. The most important outcome was alignment that current repair activity is heavily distorting cost signals, so the team will provide immediate cost visibility now while deciding separately when to engage Snowflake’s Value Engineering team for deeper optimization work.

### Meeting Flow
- The call opened with follow-up on William Wash’s warehouse analysis from the prior discussion and a recap for Partha, who missed the previous meeting. The group agreed the immediate priority is not just identifying warehouse performance issues, but fixing the specific workloads driving excessive spend.
- The discussion then drilled into the repair workload itself. The team described a very large interval-data table in Snowflake, around 30 TB, clustered on interval date/time and a channel or meter-related key. Repair queries are instead filtering on a different timestamp that is not part of the clustering, which is causing multi-hour queries and high compute use. Participants said the repair is processing roughly 600-700 million rows per day, with a small but meaningful portion of records spanning up to six months, which is creating both direct cost pressure and downstream impact on tables that read from the repaired data.
- The group clarified that this repair work is temporary and should not be treated as representative of steady-state platform cost. William said he can send Govind Srinivasan a rough cost-per-query and usage view, while Snowflake’s Value Engineering team can help later with a fuller total-cost-of-ownership and savings model, especially to quantify the benefit of improving the most expensive jobs.
- The team debated timing for that deeper analysis. Several participants noted that running a full optimization exercise before repair completes would skew the results, but Ed Murray said they could still begin discussions sooner and isolate the repair workload if needed. Partha said he would reconnect with Govind, who was out for the next two days, and the group would revisit the timing in the next meeting.
- The final portion of the call shifted to renewal logistics. Ed asked whether PPL could share the Accenture statement of work so Snowflake could try to secure funding support. The team said Govind has that document and is expected to respond. They also discussed the renewal deadline around the 23rd, noted a decision will likely be needed next week, and said a short extension through month-end is possible if necessary.

### Action Items
- **William Wash**: Send Govind Srinivasan the current cost / cost-per-query view and related report — Due: **Tuesday**
- **Partha**: Reconnect with Govind Srinivasan on whether to engage the Value Engineering team before repair is complete — Due: **next meeting**
- **Govind Srinivasan**: Reply on sharing the Accenture SOW to support funding discussions — Due: **TBD**
- **PPL and Snowflake team**: Make a renewal decision, including term length if supply chain approves — Due: **next week**

### Open Questions
- Should Snowflake’s Value Engineering team be engaged now, with repair costs isolated, or only after the repair workload is finished?
- How much of current Snowflake spend should be attributed to temporary repair activity versus normal operating usage?
- Will PPL share the Accenture SOW, and will the renewal proceed for one year or one and a half years?