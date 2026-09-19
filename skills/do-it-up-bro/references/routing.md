# Roles and fan-out

Use semantic roles, then resolve them through the host adapter and actual model access:

| Role | Useful class | Reasoning |
| --- | --- | --- |
| Director / judge | Strongest useful available | High or maximum useful |
| Hard specialist | Frontier or balanced | High |
| Implementer | Balanced | Medium or high |
| Scout / searcher | Fast sufficient | Low or medium |
| Mechanical worker | Fastest sufficient | Low or medium |

These are preferences, not permission to override user-selected models or invent host controls. If per-agent selection is unavailable, inherit the host model and disclose the limitation. Never confuse a requested model with observed execution.

Choose fan-out from the number of independent axes and host limits. Reserve capacity for integration and verification. Use deeper reasoning on bottlenecks; use faster workers for bounded leaves. Account for coordination cost and shared limits when several provider roots each create subagents.

Duplicate work deliberately only for independent reproduction, competing designs, proof attempts, consensus measurement, or adversarial search. Label the reason. Otherwise assign distinct dimensions. Close finished workers when the host requires it to free slots. Do not repeatedly retry at capacity or bypass throttling.

Use one strong agent for tightly coupled work. Use a small team for separable implementation. Use a tournament for material design uncertainty. Use native workflow facilities for large dependency graphs when supported. No provider is permanently assigned a quality rank.
