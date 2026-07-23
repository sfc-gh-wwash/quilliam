This discussion focused on sizing PPL’s Snowflake renewal, building a defensible total-cost view of the current environment, and identifying how to justify both optimization work and contract structure changes to leadership.

### Overall Summary
The meeting started with Govind clarifying that he needs a view of Snowflake cost as it exists today, not a future-state projection, and then a way to connect that spend to inefficiencies and staffing needs. The main outcome was alignment on a two-part path: first, quantify current compute/storage costs and renewal assumptions; second, use optimization findings from CoCo and a deeper value-engineering analysis to justify resources, savings, and contract decisions.

### Meeting Flow
- The group opened by clarifying scope: Govind asked for today’s total cost of ownership, and the Snowflake team explained that from a Snowflake perspective the primary cost buckets are compute and storage, with storage expected to be small relative to compute.
- Govind then explained the real business need behind the request: he wants to show leadership not only what PPL is spending, but also what is inefficient, what savings could be unlocked, and why dedicated optimization help is needed. He cited frequent long-running-query notifications and limited internal bandwidth to work through them.
- Snowflake responded by proposing two support tracks: William and team would prepare an initial breakdown, and they would also bring in Basil from the local value engineering team for a deeper ROI/TCO assessment that could be turned into a deck for leadership.
- The conversation shifted to optimization execution. William described how CoCo had already analyzed PPL metadata and generated recommendations, and the team discussed using those findings to create backlog items or Jira tickets so engineers can work through them systematically, similar to how another large customer is running a cost-savings sprint.
- The second half of the meeting moved into renewal numbers. Snowflake presented a model based on PPL’s current run rate, historical growth, planned SAP and self-service analytics workloads, and optional marketplace capacity. The proposed annual need came out to about $1.378M, with a stub-payment structure intended to lower near-term capital outlay and improve discounting.
- Govind pushed on the commercial structure, especially whether PPL can do an 18-month commitment under O&amp;M constraints and whether Snowflake’s proposed 20% discount is competitive with Databricks pricing on Azure. The group ended by agreeing to take these questions offline and reconvene after both sides do homework on pricing, capitalization, marketplace, and resale options.

### Decisions Made
- [Decision] Structure the business case in two parts: current-state cost/TCO first, then inefficiency and savings analysis to justify added resources — agreed by **Govind** and the Snowflake team.
- [Decision] Engage deeper support from Snowflake value engineering, including **Basil**, rather than rely only on a lightweight internal breakdown — agreed by the Snowflake team with customer support.

### Action Items
- **William and Snowflake team**: Break out current Snowflake cost and send the renewal model/documentation discussed on the call — Due: **TBD**
- **William / Snowflake team**: Introduce **Basil** and pursue a fuller ROI/TCO deck for PPL leadership — Due: **TBD**
- **Govind**: Check whether PPL leadership can approve an 18-month stub structure despite O&amp;M constraints — Due: **TBD**
- **Snowflake sales/deal desk**: Revisit discounting and see whether pricing can be improved in light of the Databricks comparison — Due: **TBD**
- **Govind**: Send Snowflake the Azure/Databricks published pricing reference he mentioned — Due: **TBD**
- **PPL and Snowflake**: Meet again to review Azure Marketplace and Accenture resale/capitalization options — Due: **Monday or Tuesday**

### Open Questions
- Can PPL legally and financially execute an 18-month stub-plus-renewal structure under its O&amp;M rules?
- Can Snowflake improve the proposed discount beyond 20%, especially relative to Databricks pricing on Azure?
- Would putting the deal through Azure Marketplace or reselling through Accenture create a path to capitalize more of the spend?
- How much additional consumption could come from AMI adoption and future agentic workloads that are not yet well estimated?