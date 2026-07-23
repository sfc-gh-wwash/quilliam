The meeting focused on advancing PPL’s governance and cost-management approach for AI workloads tied to Snowflake, while also working through renewal logistics ahead of month-end. The clearest outcome was alignment to pursue a supported framework through Snowflake and Accenture rather than relying on ad hoc code handoff.

### Overall Summary

Snowflake shared that it is already working with Accenture and Snowflake’s center of excellence team to build a supported cost-governance framework with Nagraj’s team. The discussion then shifted to whether PPL should build broader cross-platform observability internally or evaluate a product approach, followed by renewal mechanics, possible Azure Marketplace routing, and requests for agent-use-case examples in utilities.

### Meeting Flow

- The group opened with an update on the Accenture workstream: Snowflake has engaged its center of excellence team, which is already working with **Nagraj**’s team to build a cost-governance framework for PPL. Snowflake explained this is preferred over simply handing over code because the supported framework will be more robust and maintainable.
- The conversation then moved into what the framework should measure. **William** described Snowflake’s tagging and telemetry capabilities, including the ability to trace usage and requests at a detailed level, but noted that PPL will still need to define and collect business-value metrics such as risk reduction, operational efficiency, or revenue impact.
- PPL raised the bigger question of whether this should become an internal build in Snowflake or a purchased product, especially since agents may run across Snowflake, Databricks, Azure, and other environments. The group discussed total cost of ownership, maintenance burden, and the practical challenge of getting telemetry access from systems outside Snowflake, even though Snowflake already exposes detailed telemetry for workloads running inside its platform.
- Snowflake introduced **Natoma** as a governance option for MCP servers, describing it as a centralized layer for controlling access, securing communication, and governing usage across connected systems. The group agreed it would make sense to schedule a deeper briefing if PPL wants to explore that path.
- The final major topic was the renewal. Snowflake asked for a redacted Accenture SOW or equivalent evidence showing Snowflake-related work so renewal funding could potentially be applied to it, and also asked whether the order could go through Azure Marketplace. PPL said the documentation request seems feasible, but marketplace routing would need procurement review. The meeting closed with a request for examples of utility-focused agents and AI use cases, including AMI pattern-recognition work already being discussed internally.

### Decisions Made

- [Decision] Pursue a supported cost-governance framework through Snowflake’s COE and Accenture, rather than relying on unsupported code delivery — agreed by Snowflake and PPL.

### Action Items

- **Govind**: Provide redacted SOW details or equivalent line-item information showing Accenture work tied to Snowflake usage — Due: **TBD**
- **Ed / Bill**: Arrange a deeper **Natoma** briefing for PPL if they want to explore MCP governance further — Due: **TBD**
- **Ed**: Reach out to **Fred Cohagen** for utility-specific agent examples/use cases and share material offline or set up follow-up time — Due: **TBD**
- **Snowflake team**: Connect with **Govind** on renewal details and Azure Marketplace/procurement options — Due: **23rd**

### Open Questions

- Should PPL build the broader governance/observability capability inside Snowflake or buy a product instead?
- How quickly can PPL get access to telemetry from agents running outside Snowflake or through external MCP-connected environments?
- Can the renewal be routed through Azure Marketplace, and what procurement steps would be required?