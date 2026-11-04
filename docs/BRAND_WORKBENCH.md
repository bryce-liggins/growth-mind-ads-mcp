# Build and maintain a brand workbench

A brand workbench gives the agent the business understanding it needs to make useful recommendations. It preserves the customer's situation, the owner's strategic choices and reasoning, product reality, creative judgment and evidence across linked Markdown files.

The [9-file starter](../examples/brand-workbench/README.md) distills Growth Mind's workbench structure for this playbook. It is a reusable template, not a copy of private client context. The bridge does not automatically discover or load it: your agent instructions must point to the private workbench's README.

## 1. Reuse or create the private workspace

Ask where the owner keeps authoritative business documents. If a workbench already exists, map its files to the starter's responsibilities and fill genuine gaps. Preserve owner edits and source history. Avoid a second editable brand rulebook.

Otherwise, copy `examples/brand-workbench/` into the owner's chosen private document workspace. From the repository root, after selecting an unused destination:

```sh
mkdir -p /absolute/path/to/private-business-workspace
cp -R examples/brand-workbench /absolute/path/to/private-business-workspace/brand-workbench
```

Replace the example path and verify the destination does not already exist before copying. Keep completed files outside a public clone/fork. Use separate workbenches for distinct brands; the same company may have multiple customers, offers and voices.

### Consolidating an existing starter

If you filled in the earlier starter, merge overview and status into README.md, creative-library content into asset-inventory.md, and source-map content into decisions.md. Preserve source IDs, dates, owner edits and substantive sections; resolve conflicts before retiring the old files. Update links and agent inputs to the consolidated locations. Keep any needed historical copy as private source evidence, not a second current rulebook.

## 2. Build from evidence before interviewing

Read the owner's existing context, approved brand/product materials and relevant customer research. Inspect representative official pages and published creative when access is authorized. Record what you actually inspected in decisions.md, including dates and limits. Preserve substantive examples, exceptions and product nuances, not just summaries.

Route identity to README.md, current offers to offering.md, outcomes and reasoning to goals.md, customer understanding/positioning to brand-foundations.md, creative judgment to taste.md, design rules to visual-system.md and metric definitions to performance.md. Keep live priorities in README.md. Record decisions and conflicts in decisions.md. Keep the asset library, retrieval instructions, review process and individual records together in asset-inventory.md.

Fill every file with useful sourced content or a specific gap and next source. Replace template metadata with the brand, actual dates and appropriate review state. A populated template is still a draft until its consequential direction is confirmed. Do not infer the owner's objective from the website or invent an emotional insight because it sounds plausible.

## 3. Draw out the owner's judgment

Ask one question at a time, using existing answers first. Prioritize the missing decision that changes the next recommendation. Useful questions include:

- What outcome matters most for this account right now, and what tradeoff are you willing to make for it?
- Which customers look relevant in a keyword report but are a bad fit for your business, and why?
- Should this campaign pursue competitor searches, avoid them, or treat particular competitors differently?
- Show me an ad or page you would approve and one you would reject. What makes the difference?
- What does a qualified lead mean here, and when do you know whether one became a customer?

Save the actual answer, reasoning, date and scope. Ask for direction when it is missing; routine drafting can continue within decisions already made. Proposals stay labeled as proposals.

## 4. Check that context changes the recommendation

Use a short dry run before account analysis. These examples are fictional and do not prescribe your strategy.

| Scenario | Workbench evidence | Expected agent behavior |
| --- | --- | --- |
| Query: `RivalCo repair near me` | offering.md says this campaign does not pursue competitor demand; decisions.md records why | Propose an exclusion for review, inspect match/scope/conflicts and show demand at risk. Do not apply it. |
| Same query, another campaign | goals.md selects competitor acquisition within an agreed scope | Evaluate it against that objective; do not exclude it just because it names a competitor. |
| Low-volume term for an unsupported service | offering.md confirms the service is not sold | Identify the business mismatch even when conversion evidence is sparse. |
| Repeated headline appears to win | performance.md records directional pooled observations; taste.md records owner examples | Explain evidence limits, then propose a challenger grounded in the owner's positioning and voice. Preserve the marketer's creative judgment. |
| Build a matching landing page | offering, foundations, taste, visual and asset files plus performance.md | Match intent and promise, use the approved creative system, and carry measurement requirements into the build. |

For each recommendation, cite the file/section and source or decision that supports it. If changing the business goal never changes the recommendation, revisit how context is being used.

## 5. Connect it to the agent's workflow

Use [the README routing table](../examples/brand-workbench/README.md#read-only-what-the-job-needs). Have the agent read the README, current status and applicable decisions first, then the files needed for that task. Place the absolute private README path in your project instructions or operating prompt. Do not paste the whole folder into every request.

For shell-restricted/headless sessions that cannot read local files, the scheduler wrapper must insert the relevant files' actual contents into the prompt, labeled with paths and revision dates. A path or a summary alone is insufficient. Record which revision each run used, and refresh that input after accepted changes. See [SCHEDULING.md](SCHEDULING.md).

## 6. Maintain the workbench as the work changes

When an owner corrects a recommendation, capture the correction and why in decisions.md. Update the file that owns the rule, link the decision/source and preserve the previous rule as dated history. Refresh source coverage and affected workflow inputs. Do not turn a campaign-specific decision into a universal policy.

Record experiment observations in performance.md and changing priorities in README.md. Results can support a proposed strategy or creative change; a winning ad alone doesn't rewrite brand rules. Resolve conflicting guidelines explicitly, preserving the evidence on both sides. Continue unaffected work while the owner settles the material choice.

## Agent prompt

```text
Build or improve my private brand workbench using this repository's
examples/brand-workbench/README.md and docs/BRAND_WORKBENCH.md.
First inspect the business documents and existing workbench I authorize.
Reuse the existing structure if it covers the same responsibilities.

Preserve customer insight, my strategic choices and why I made them,
product/offer details and limits, goals, voice examples, visual rules,
metric definitions, sources and decisions across linked Markdown files.
Use real examples and source dates. Label confirmed, observed, proposed,
unknown and conflicting content. Do not invent missing strategy or proof.
Keep completed business context private and separate from the public repo.

Show what you found, what is usable and the next missing decision.
Ask me one question at a time where my judgment is needed.
Before account recommendations, confirm the objective, success metric,
demand policy and constraints for the relevant campaign scope.
Demonstrate a sample search-term decision and an ad/page brief that cite
the workbench rules behind them. Do not make account changes.
```

## Handoff acceptance

Return the private README path, file inventory, source coverage, owner-confirmed direction, remaining questions and dry-run outputs. Report which workflows are ready and which depend on missing context. An incomplete visual library can coexist with a usable search-term workflow. Missing strategic direction holds the affected recommendations. Business context never replaces exact account-change approval.
