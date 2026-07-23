Here’s a concise summary of the discussion about Richard’s governance and FinOps solution and its possible fit for customer work.

### Overall Summary
Prathamesh brought William and Richard together to review a solution Richard built that could help with the PPL account, where Accenture is asking for guidance on data governance, FinOps, AI governance, observability, and reporting. The main outcome was that Richard’s demo looked highly relevant, but he will first check with leadership and the AI Council before sharing or packaging it more broadly.

### Meeting Flow
- Prathamesh opened by explaining that the PPL account needs guidance in areas including data governance and FinOps, with Accenture involved. William added that PPL is Pennsylvania Power and Light, a utility company, and said several customers are now asking for similar capabilities around AI governance, observability, reporting, and FinOps.
- Richard walked through an admin dashboard he built over roughly the last three months. He said it runs in his demo account with synthetic data and gives visibility across accounts under an org ID or global admin view, including live accounts, cloud providers, warehouses, query activity, and usage trends.
- Richard then showed governance-focused views: catalog and database visibility, ownership, business glossary/semantic layer elements, popularity and usage, governance controls, masking policies, compliance policies, and where sensitive data protections are or are not in place.
- He also covered AI governance and FinOps features, including “tokenomics,” Cortex feature usage, model economics and run rates, who in the organization is using AI, optimization logic, agent configuration concerns, and a model bake-off capability that compares price, performance, and accuracy across models. He noted Snowflake Intelligence is embedded with contextual prompt suggestions.
- The discussion shifted to sensitive data, lineage, and unstructured data. Richard described discovery across accounts, identification of PII such as emails, phone numbers, and Social Security numbers, masking coverage, lineage tracking, data sharing, health scoring, and a knowledge graph.
- Finally, the group discussed chargeback design. Richard’s current mechanism is account-level, based on how EY Fabric handles it today, while William and Prathamesh discussed a tag-based/project-based approach for teams such as Accenture working on PPL. The main concern was how to standardize tagging and avoid gaps; Richard suggested a possible role/group-based alternative.

### Decisions Made
- [Decision] Richard will wait for feedback from leadership and the AI Council before sharing or distributing the solution more broadly — agreed by **Richard**, accepted by **William**.

### Action Items
- **Richard**: Check leadership and AI Council status, confirm how the solution can be shared/adopted, and update **William** and Prathamesh — Due: **TBD**

### Open Questions
- Can Richard’s solution be approved, packaged, and distributed beyond his current book of business?
- For customer chargeback, should allocation be account-based, tag-based, or role/group-based?
- Can partners standardize tagging well enough to support project-level chargeback without gaps?