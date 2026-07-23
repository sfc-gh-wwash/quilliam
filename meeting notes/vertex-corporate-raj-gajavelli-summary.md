Here’s a concise summary of the meeting.

### Overall Summary
William Wash advised Raj Gajavelli on how to improve and operationalize Snowflake Cortex Agents for an executive-facing customer briefing use case through Microsoft Copilot. The main outcome was alignment on the near-term setup: tune the agent configuration, use Microsoft Entra with SCIM for executive provisioning, and follow up separately on the right network policy and VPN model for executive access.

### Meeting Flow
- Raj opened by describing two published agents in Microsoft Copilot, including a customer briefing agent intended to give executives a high-level customer summary before meetings. He asked about login behavior, and William explained that access would likely rely on an OAuth token that may persist for some time but eventually expire and require reauthentication.
- The conversation then shifted to slow response times. William recommended testing the same prompt directly in Snowflake to separate Copilot-to-Snowflake latency from agent execution latency. Using trace data, they reviewed planning time, SQL execution time, and response-generation time, and William suggested optimizing SQL, semantic views, and warehouse sizing where relevant.
- William then showed Raj how to improve the customer briefing experience by adding explicit agent skills and instructions. He recommended using Cortex Code to generate a skill that defines exactly how the agent should answer customer-summary requests, including specific queries, tools, output structure, and HTML formatting.
- While reviewing the agent configuration, they found the orchestration timeout was set too low. Raj updated it to 300 seconds, and William recommended materially increasing the token budget so the agent would not run out of tokens during richer responses.
- Raj next described the planned role hierarchy and the need to publish the experience to executives who do not already have Snowflake logins. William recommended handling provisioning through Microsoft Entra and SCIM, mapping Entra groups to Snowflake roles so users are automatically created and assigned the correct role when added to the appropriate group.
- The rest of the meeting focused on security and operations: MFA expectations, break-glass access, network policies, and usage tracking. William recommended MFA primarily for elevated admin users, suggested maintaining a break-glass account with key-pair authentication, clarified that `0.0.0.0` represented Snowflake internal/serverless activity rather than unrestricted public access, and showed Raj where to monitor agent token and credit usage through account usage and AI observability data.

### Decisions Made
- [Decision] Increase the agent orchestration timeout to **300 seconds** — agreed by **Raj** with confirmation from **William**.
- [Decision] Use Microsoft Entra group mapping and SCIM-based provisioning for executive rollout — agreed by **William** and **Raj**.
- [Decision] Keep MFA requirements focused on users with elevated administrative privileges rather than all executive end users — recommended by **William** and accepted in principle by **Raj**.

### Action Items
- **William Wash**: Email **Raj Gajavelli** the Entra/SCIM setup links and additional guidance on network policy and VPN handling for executive users — Due: **TBD**
- **Raj Gajavelli**: Begin the Entra/SCIM provisioning setup for executives and involve the Vertex IT engineering team — Due: **next week**
- **Raj Gajavelli**: Re-enable and implement a break-glass service account using key-pair authentication — Due: **TBD**
- **William Wash**: Share the credit-usage dashboard/work once it is in a usable state and published to Git — Due: **TBD**

### Open Questions
- How long the OAuth token persists before users are prompted to sign in again
- Whether executive users accessing the agent through Copilot need VPN-based IP restrictions, and if so, which policy should apply
- The exact network-policy model to use for executive Copilot-only users versus elevated Snowflake administrators