Joseph walked **William** through a proposed Snowflake warehouse consolidation and migration plan aimed at reducing warehouse sprawl and lowering compute costs while minimizing operational risk.

### Overall Summary
The meeting focused on Joseph’s phased approach to moving assets onto consolidated warehouses, validating the approach in pre-production, and folding the results into FinOps tracking. The most important outcome was alignment on the migration direction: start with a limited test on a new product or asset, then expand toward broader migration and retirement of unused warehouses.

### Meeting Flow
- Joseph described a phased consolidation plan in which “phase two” would actually happen first: put a new asset or product onto consolidated warehouses to test how the approach works before wider rollout.
- He said he does not want to remove anything that might still be in use, so the original “phase one” may effectively become a later cleanup phase. That later work would include granting role access, making Terraform and repository changes, migrating current assets in the Snowflake account, validating they run correctly in Pepper, and then retiring old migration and zero-usage warehouses.
- Joseph said the plan also includes adding resource monitors and incorporating the work into FinOps measurement. He estimated savings of roughly 1,500-2,500 credits per month, which he framed as about $100K annually and nearly $300K over three years. He also noted uncertainty around staffing and said he may have to do the work himself if no resources are assigned.
- Joseph confirmed he intends to do the work in pre-production first. The conversation then shifted to a Fidelity Investments example Joseph had been trying to reference; he said the presentation was not posted and the Fidelity sponsor did not respond, though the claim presented was that Fidelity runs only five to seven warehouses in production. **William** was skeptical and said conference examples are often more aspirational than operational, especially for a company like Fidelity.
- At the end, **William** asked whether the on-demand migration effort was still active. Joseph said it was still ongoing, but he had not been involved recently because nothing had been urgent in the last two weeks. He also mentioned a separate production recommendation identified through his FinOps dashboard and adjusted through Cortex, and said he would ask about it in a 4 PM meeting.

### Decisions Made
- Pre-production will be the first environment used for the warehouse consolidation and migration work — agreed by **Joseph**.
- The rollout will begin with a limited test on a new asset or product before broader migration and cleanup — agreed by **Joseph** and acknowledged by **William**.

### Action Items
- **Joseph**: Start the consolidation effort with a pre-production test on a new asset or product — Due: **TBD**
- **Joseph**: Progress later migration phases, including access changes, Terraform or repo updates, asset migration, validation in Pepper, and retirement of unused warehouses — Due: **TBD**
- **Joseph**: Ask in his 4 PM meeting whether the production team should reach out to **William** regarding the transaction-related recommendation or related migration follow-up — Due: **4 PM**

### Open Questions
- Will Joseph receive additional resources for the consolidation work, or will he need to complete it himself?
- Is the Fidelity Investments example accurate in practice, and is there any supporting presentation or evidence available?
- What is the concrete plan for the separate on-demand migration effort, and who is expected to involve **William**?