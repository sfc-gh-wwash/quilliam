The team met to define how a Snowflake-Hakoda CoCo hackathon could create a fast, credible win for iPipeline.

### Overall Summary
The discussion centered on choosing a hackathon use case that would prove value quickly for iPipeline while also addressing internal resistance from its data engineering team. The clearest outcome was to pause ideation on a specific build and instead get direct input from **Seth Roy** before locking the scope, audience, and team involvement.

### Meeting Flow
- The group started with introductions, then reviewed iPipeline’s account context: iPipeline is an insurance software company working through a migration from AWS and Iceberg-oriented architecture toward Snowflake because of scalability, performance, and cost issues. The team noted that Snowflake and Hakoda are working mainly with a product-side champion, while the data engineering team has been resistant to outside help.
- They framed the CoCo hackathon as a way to build an agent or lightweight data product that demonstrates tangible value quickly and helps show that iPipeline cannot realistically execute the broader migration and AI opportunity alone. The goal was less about a perfect use case and more about something feasible with available data in an afternoon or day.
- The team then unpacked the account’s political context. After iPipeline’s acquisition by Roper Technologies, the account shifted toward AWS-centric thinking and lost momentum on Snowflake value creation. Michael Beaver said the business side wants to move faster, while the data team is acting as a blocker despite already having data in Snowflake.
- William Wash explained the usable data: it reflects the insurance application lifecycle across carriers and could support insights such as agent effectiveness, carrier routing, and placement patterns. However, only one product has been migrated so far, seven more remain, and the current model is largely flexible VARIANT/JSON data with only some common fields, so any semantic layer would likely require flattening views first.
- The group debated whether the hackathon should prioritize an external-facing product for carriers or an internal capability for the data team, such as schema mapping, data quality checks, alerts, or lifecycle automation. William argued for giving **Seth Roy** something sellable while also showing the data team how CoCo can accelerate delivery; a possible compromise was a pipeline that flattens data, adds data quality functions, and layers semantics on top.
- The conversation ended with concern that brainstorming had outpaced the known facts. The team also flagged Sigma adoption as an outlier issue at iPipeline, but agreed that this should be a separate follow-up topic rather than the basis for the immediate hackathon plan.

### Decisions Made
- [Decision] Use a direct conversation with **Seth Roy** as the immediate next step before committing to a specific hackathon use case or participation model — agreed by the group.

### Action Items
- **Michael Beaver**: Speak with **Seth Roy** and get the broader group aligned on a concrete hackathon direction, including whether version one should work directly with product and potentially exclude the data engineering team — Due: **Thursday**
- **Michael Beaver**: Clarify whether the product organization would have sufficient access to execute if the data engineering team is not involved in the first version — Due: **TBD**

### Open Questions
- Should the first hackathon use case be external-facing for carriers or internal-facing for data quality and delivery acceleration?
- Should the data engineering team be excluded from version one to avoid early friction?
- Is there enough accessible Snowflake data and user access on the product side to execute without the data engineering team?
- Why is iPipeline seeing weak Sigma adoption, and what data is currently exposed through it?