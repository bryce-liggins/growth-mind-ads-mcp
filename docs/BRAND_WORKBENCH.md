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

## 2. Guide the owner through source discovery

Begin with one easy question: "Do you have brand guidelines, an existing brand workbench or other business materials we can start with?" Skip it if the owner has already answered. Wait for the answer before asking another question.

If materials exist, help the owner locate or share them through the available file/link tools, then read them. Reuse an existing workbench and preserve its edits. If no materials exist, or relevant gaps remain, ask: "May I review and scrape your official website to build a first picture of the brand?" Ask for the URL separately if it is unknown. Use permission already given for that scope; don't ask again. If permission is declined or access/tools are unavailable, explain the limitation briefly and continue the interview. A website is helpful, not required.

Within the authorized scope, inspect representative home, product/service, about and conversion pages, relevant published examples and available design evidence. Keep discovery bounded to the business and this workbench. Do not buy a scraping plan, expand to private sources or bypass access controls. Record exactly what was inspected, source dates and access limits in decisions.md. Preserve substantive examples, exceptions and product nuances. Label published claims and inferred brand patterns as observations until their applicability is confirmed.

Summarize what you learned in plain language and identify the remaining information gaps. This should orient the owner, not give them a questionnaire to complete. Ask only the next useful question.

## 3. Interview one question at a time and build as you go

Use existing sources and answers before asking anything. Ask one focused question, wait for the answer, update the appropriate files, then choose the next question from what is still missing. Ask a follow-up when the reasoning, example or scope would materially improve the work. Avoid bundling several questions into one message or marching through a fixed checklist when the answer is already available.

Use this coverage map internally. Example questions are alternatives to ask individually, not a form to send all at once.

| Information to establish | Example next question | File |
| --- | --- | --- |
| Business scope and current situation | Which part of the business should this workbench support first? | README.md |
| Customer and buying trigger | What usually happens just before your best-fit customer looks for you? | brand-foundations.md |
| Offering, limitations and demand | Which requests look relevant but are a poor fit for your business? | offering.md |
| Goals and tradeoffs | What outcome matters most for this account right now? | goals.md |
| Strategic reasoning | Why is that the priority now? | goals.md, decisions.md |
| Competitor-demand policy | Should this campaign pursue competitor searches or avoid them? | offering.md, decisions.md |
| Voice, taste and proof | Can you share one piece of copy you like and explain what works about it? | taste.md |
| Visual direction and assets | Which existing page or asset best represents the look you want? | visual-system.md, asset-inventory.md |
| Success definitions and measurement | What makes a lead qualified in your business? | performance.md |
| Capacity, constraints and responsibilities | What operational limit should shape our recommendations? | goals.md, README.md |

Save the owner's language, reasoning, date and scope. Ask for counterexamples or rejected creative when useful. Keep source records and integration coverage in decisions.md, and live priorities/open loops in README.md. Keep the asset library, retrieval instructions, review process and individual records in asset-inventory.md.

Maintain a compact gap list in README.md: topic, known evidence, missing detail, affected workflow and next question. An owner may answer "I don't know" or defer a topic; record that explicitly and continue useful work. Do not invent a target, brand rule, customer motivation or strategy to make every field look complete. Don't claim all the owner's knowledge has been captured.

Build the nine files as answers arrive. Fill each with useful sourced content or a specific gap. Replace template metadata with the actual brand, dates and review state. Confirm consequential choices in short summaries, especially the goal, success definition, demand policy and constraints. Before the handoff, show the workbench and ask: "What should we correct or add before using this?" Save corrections and remaining gaps. If interrupted, save the interview checkpoint and resume from the next unanswered question without restarting.

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
examples/brand-workbench/README.md and docs/BRAND_WORKBENCH.md. Guide me through the process one question at a time.
Wait for my answer before asking the next question. Reuse answers,
materials and permissions I have already provided.

Start by asking whether I have brand guidelines, an existing workbench
or other business materials to use. If I do, help me share or locate
them and read them first. If I don't, or they leave gaps, ask permission
to review and scrape my official website. Ask for the URL if needed.
If I decline or you can't access it, continue with my answers.

Summarize what you've learned and the gaps that remain. Interview me
one question at a time to fill them. Cover the customer and buying
situation, offering and limits, goals and tradeoffs, voice and examples,
visual direction and assets, performance definitions and constraints.
Ask for my reasoning and real examples when they would clarify a choice.
Don't ask me to repeat information you already have or send a long form.

Build the linked Markdown files as we go. Preserve my language and
reasoning, source dates and decisions. Label confirmed facts,
observations, proposals and unknowns. Don't treat website copy as my
confirmed strategy. Keep a list of unresolved gaps so we can resume.

Show me the resulting workbench and ask what needs correcting or adding.
Before account recommendations, confirm the objective, success metric,
demand policy and constraints. Show a sample search-term decision and
an ad or landing-page brief grounded in the workbench.
Keep my completed workbench private. Do not make account changes.
```

## Handoff acceptance

Return the private README path, file inventory, source coverage, owner-confirmed direction, remaining questions, interview checkpoint and dry-run outputs. Confirm that the source-discovery path respects existing permission, a no-guidelines owner can proceed, declined/unavailable website access falls back to the interview, and returning owners are not asked to repeat saved answers. Report which workflows are ready and which depend on missing context. An incomplete visual library can coexist with a usable search-term workflow. Missing strategic direction holds the affected recommendations. Business context never replaces exact account-change approval.
