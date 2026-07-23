This discussion focused on how to expose Snowflake semantic data to agents while preserving entitlement, security, and metadata governance.

### Overall Summary
The team aligned on two related goals: building a “semantic MCP gateway” so internal or partner-built agents can query governed semantic data, and using that gateway to power an initial “data concierge agent” in Vertex Copilot. William demonstrated how Snowflake agents can support multi-tenant access, domain-specific tools, and governed query execution, while the broader discussion focused on where entitlement checks and Atlan-based metadata should live in the architecture.

### Meeting Flow
- The meeting opened with a reset on scope: the team wants to expose semantic assets from domains like O-Series and Certificate Center to agents, then use the same capability as the foundation for a first-party data concierge agent. The main requirement is secure, entitlement-aware access to semantic data across domains.
- **William** showed a Snowflake multi-tenant agent pattern using session context plus row-level security and related governance controls. In the demo, the same agent returned different results for different client contexts, illustrating how tenant-specific answers can be enforced without changing the core query flow.
- The group then explored architecture options for multi-domain access. A central concern was avoiding a large “blast radius” where one agent could reach data a user should not see. **William** recommended thinking in terms of domain or product-specific agents/tools, with a router or proxy deciding which agent/tool can be invoked based on entitlement and question context.
- The conversation shifted to metadata and discovery. **William** explained that Snowflake agents work best when querying curated semantic views, while broader data discovery increases hallucination risk. He showed a fallback pattern where the agent first tries the semantic view, then queries **Atlan** through MCP only when needed, logs those misses, and uses that signal to decide what should eventually become a curated semantic view.
- The final part of the meeting focused on operationalizing the approach. The team discussed evaluation datasets, observability, thumbs-up/down feedback, and long-term options for bringing **Atlan** metadata closer to Snowflake rather than relying only on live MCP lookups. They closed on a fast-turn prototype plan for leadership, likely spanning a few datasets across two domains.

### Decisions Made
- [Decision] The near-term deliverable will be a prototype rather than a comprehensive solution — agreed by the team.
- [Decision] The prototype should demonstrate cross-domain semantic access with entitlement controls, likely across two domains — agreed by the team.

### Action Items
- **William**: Share a graph/call-flow view of the current interaction pattern as a starting point for the reference architecture — Due: **TBD**
- **William**: Send an email with his calendar link so the team can book follow-up working sessions — Due: **TBD**
- **Dan**: Sketch the reference architecture, especially entitlement enforcement, context injection, and the **Atlan** integration path — Due: **mid to late this week**
- Data platform team: Align on next steps and start a quick prototype for leadership review — Due: **third to fourth week of July**

### Open Questions
- Should metadata context be pulled live from **Atlan** via MCP on demand, or pushed into Snowflake through a longer-term pattern such as a lakehouse-style metadata sync?
- Where should entitlement enforcement live in the final architecture: proxy/platform layer, agent/tool discovery layer, or both?
- How should special “agent access” entitlements be modeled if product access and agent access become separate commercial controls?