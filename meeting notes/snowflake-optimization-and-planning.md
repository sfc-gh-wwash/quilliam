The meeting focused on two near-term priorities: addressing a large transactional/VOD pipeline that is expected to grow significantly, and aligning on how Snowflake can help Vertex with optimization, Azure migration, compliance, and AI-assisted engineering workflows. The most important outcome was agreement to form a working group around the pipeline issue and to start structured planning now so the team can show measurable progress ahead of renewal discussions in early October.

### Overall Summary

The group discussed a major pipeline that is already the biggest technical concern and will expand further as more VOD customers are onboarded. They also explored where Snowflake can provide practical help beyond platform tuning, including funding, services, compliance implementation support, and enablement around Cocoa for pipeline development and automation.

### Meeting Flow

- The conversation opened on a large transactional pipeline that may need more than warehouse sizing changes; the concern was framed as a deeper data architecture or processing-methodology problem. Rather than handling it offline, the group agreed to create a working session with the right people involved.
- The team then shifted to strategic planning for renewal and Azure migration. Vertex wants a stronger optimization story by early October, with visible usage improvements and a clearer view of where Snowflake investments or support can accelerate priorities.
- A substantial portion of the meeting covered data residency and sovereignty. The discussion clarified that the answer depends on how strict the business requirement is: if data cannot leave a region, separate end-to-end regional environments are likely required; if anonymized or aggregated data is acceptable, cross-region reporting patterns may still work.
- The group reviewed SOX readiness and agreed that making the full production environment SOX-compliant is simpler than selectively applying controls. Snowflake can explain implementation options, but compliance advice itself would need to come through services or the customer’s compliance team.
- The conversation then moved to Cocoa as an engineering accelerator. William explained that Cocoa can support Snowflake work, DBT pipelines, Jira/MCP workflows, PR generation, and related automation, and the group discussed using a real product effort as a proof of concept.
- The meeting closed with interest in a joint Snowflake-Atlan conversation/semantic demo for executives, plus a separate follow-up request to identify the right Vertex alliance contact for a proposed tax data hub effort.

### Decisions Made

- [Decision] Create a dedicated working group for the large pipeline issue rather than leaving it to offline follow-up — agreed by the group.
- [Decision] Treat full production SOX compliance as the operating direction rather than selectively scoping only certain systems — agreed by the customer team.
- [Decision] Use a focused proof of concept to evaluate Cocoa on a real pipeline/product effort — agreed by the group.

### Action Items

- **Alan** and **Joe**: Lead the pipeline working group and pull in additional contributors such as Swapnil as needed — Due: **TBD**
- **The customer team**: Send calendar options and schedule a session for the pipeline deep dive next week — Due: **next week**
- **William**: Share Cocoa quick-start materials and set up a working session/demo for the team — Due: **TBD**
- **Kiran** and **Ed**: Coordinate the best format for broader Cocoa learning sessions — Due: **TBD**
- **William**: Follow up with the Atlan team and return with a joint proposal/message — Due: **next week**
- **Customer team**: Email details on the tax data hub/alliance request so the right Vertex contact can be identified — Due: **TBD**

### Open Questions

- How much of the large VOD/transactional pipeline problem is fixable through Snowflake optimization versus deeper architectural redesign?
- What exact data residency standard will the business require: regional storage only, no cross-region copies at all, or a more flexible anonymized/aggregated model?
- Where is the clearest boundary between using Cocoa versus more general coding tools for Vertex’s engineering workflows?