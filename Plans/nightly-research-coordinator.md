# Future plan: nightly research coordinator

Status: proposed, 2026-10-02. Not implemented or scheduled by this plan.

## Purpose

Run research on the dedicated Mac Mini each night, produce readable results with
visualizations, and suggest useful next experiments. Keep it easy to discuss the
results in Codex or Herdr and use different models for implementation, review,
and advice.

The first version coordinates the existing research workflow. It does not replace
the experiment records or overnight queue, and does not require a new database,
dashboard, or separate research-manager application.

## What already exists

- `Plans/` holds experiment plans and handoffs.
- Track notebooks and experiment documents record results and interpretation.
- Track `findings.md` files hold reviewed, consolidated claims.
- `scripts/run_queue.py` and `scripts/queue_lib.py` execute the overnight queue and
  maintain its status, locking, logs, and per-run metadata.
- `scripts/summarize_runs.py` provides a separate Claude-based summary step.
- `experiments/output/` holds raw results, logs, metadata, and generated reports.
- Experiment scripts already produce analysis tables and can generate plots.
- `docs/methodology.md` and the research-rigor workflow define research review
  and claim-promotion requirements.

See [the queue design](overnight-queue-runner.md) and
[pivot night 2](map-bias-pivot-night2.md) for existing execution patterns.

## What is missing

A coordinator that connects these steps reliably:

1. Select experiments from an agreed backlog.
2. Prepare necessary code changes and obtain independent code review.
3. Validate and launch the existing queue.
4. Check completion and analyze results.
5. Generate visualizations and review the interpretation.
6. Write a morning briefing and propose the next experiments.
7. Save decisions from the subsequent discussion into the existing research files.

Chat history should help the conversation, but the files must contain enough
context for a fresh agent to continue the program.

## First-version workflow

### Research direction and backlog

Keep a short Markdown program document with the current high-level question,
open explanations, relevant prior results, candidate experiments, and agreed
limits. Reuse a suitable existing plan where possible.

Each backlog candidate should state:

- The question it answers and why it matters now.
- The competing explanations it distinguishes.
- The proposed conditions, baselines, seed counts, and measurements.
- What different outcomes would mean, including an inconclusive result.
- Expected compute and model effort, dependencies, and priority.
- Whether it is approved to run or remains a proposal.

Start by selecting from approved candidates. An empty approved backlog produces
a request for direction and useful proposals, rather than an invented overnight
run merely to keep the machine busy.

### Preparation and execution

For an experiment that needs code changes, prepare them in an isolated checkout,
run the relevant checks and a small timing/smoke pilot, and obtain the configured
independent code review before launching. Freeze the execution commit and
configuration and follow the repository's commit/publication conventions.

For an experiment using an already reviewed harness, avoid repeating a code-review
cycle unless code or relevant requirements changed. Still validate its new queue
and configuration.

Execute through the existing queue runner. Schedule the coordinator on the Mini
so nightly execution does not depend on an open laptop or an active conversation.
Reuse existing queue bookkeeping; add only the coordinator state needed to resume
preparation, analysis, and reporting without duplicate actions.

Use one active execution queue per checkout/output namespace, bounded worker
counts, wall-clock limits, and process cleanup. Leave partial data intact when a
run fails. Diagnose before retrying; do not silently restart a failed experiment
or change its scientific settings to make it finish.

### Completion and analysis

An exit code of zero or a DONE marker is insufficient by itself. Check the
expected arms, seed coverage, row counts, duplicate keys, configuration, execution
commit, and missing outputs. Track-specific validation remains in the experiment
harness; the coordinator invokes it and records its outcome.

Analyze complete and partial results with their actual denominators. Preserve
the distinction between observed task success, generalization, and proposed
mechanisms. Perform winner/shortcut inspection when required by the research
workflow. Any implementation repair after launch must retain its provenance and
the original rows, as in pivot night 2.

### Results review and morning report

Give the independent results reviewer the experiment plan, configuration, code
reference, raw measurements, analysis, plots, and draft interpretation. A prose
summary alone is not enough evidence.

Resolve actionable findings before presenting the report as reviewed. If the
reviewer is unavailable or the review budget is exhausted, retain the draft and
show the pending review explicitly. Findings promotion follows the track's
existing gates; a morning report does not automatically promote a claim.

The morning briefing should be short enough to read over breakfast:

1. What we tested and why.
2. What happened, with the important numbers and two or three useful plots.
3. What this teaches us, within the tested scope.
4. Failures, incomplete data, uncertainty, and reviewer disagreements.
5. Up to three suggested next experiments, ranked with reasons and estimated
   effort.

Keep the detailed notebook as the research record. Generate the readable briefing
and charts from the same analysis artifacts, with links to the plan, notebook,
raw results, and reviews. A Markdown briefing is sufficient initially; an HTML
page or simple blog can follow without changing the execution workflow.

## Discussion and visualization

Use one continuing research conversation per program in Codex or Herdr. The agent
should be able to answer questions about a specific experiment, compare it with
earlier runs, explain a chart, challenge an interpretation, and revise priorities.
Save resulting decisions and their reasons in the program plan or notebook.

Generate scientific plots with the existing plotting tools. Choose charts for the
question being tested: solve rates with uncertainty, paired differences, fitness
trajectories, population diversity, runtime, or failure categories. Show actual
sample sizes and missing data; label proxies and exploratory analysis.

Later, interactive comparisons could let the user select experiments, maps,
budgets, seeds, or model roles. A dashboard is optional and should follow a
working nightly loop, rather than become a prerequisite.

## Configurable models and review roles

Keep provider, model, reasoning settings where supported, timeout, and review
budget configurable per role:

| Role | Responsibility |
| --- | --- |
| Planner | Propose and prioritize experiments, explaining their value |
| Implementer | Prepare code, checks, and execution configuration |
| Code reviewer | Independently inspect correctness and reproducibility |
| Results reviewer | Challenge statistics, shortcut solutions, and claim scope |
| Adviser | Offer another interpretation or research direction when useful |
| Writer | Turn reviewed evidence into a readable briefing |

Roles may use different models or providers. Use independent review sessions and
record the actual reviewer identity, assessed code/report version, findings, and
resolution. Named reviewers such as Fable must resolve to an actual configured
model or agent; another reviewer must not be presented as that named reviewer.

Avoid calling every model on every step. Routine experiments need the relevant
code review, results review, and report. Additional advice is most useful when
results are surprising, reviewers disagree, or the next direction is unclear.
Model agreement is not a substitute for measured evidence.

## Autonomy and limits

Introduce autonomy gradually:

1. **Approved backlog:** automate preparation, execution, validation, plots,
   review, and reporting for agreed experiments. Suggest new experiments for
   discussion.
2. **Bounded selection:** let the coordinator choose among approved candidates
   within an agreed research scope and nightly budget.
3. **Bounded experiment creation:** later permit it to propose and launch new
   experiments within explicit limits on scope, resources, code changes, and
   review requirements.

Agree on the nightly execution window, compute budget, model-spend or usage
limits, allowed roles/providers, maximum review rounds, retry policy, and stop
conditions before enabling the first scheduled run. Enforce available limits in
code rather than relying solely on prompts. Report unavailable cost accounting
honestly instead of promising a monetary cap the provider cannot enforce.

Stop and preserve work on unresolved methodological defects, review failure,
budget exhaustion, unexpected scope changes, or repeated infrastructure failures.
Notify on completion, failure, or a needed decision; remain quiet during ordinary
unchanged progress.

## Relationship to ptc manager

Begin in folding-evolution, using its existing queue and research conventions.
Herdr remains useful for access and agent sessions. The coordinator owns the
research sequence and durable handoffs, not a new terminal-management system.

Ptc manager already has useful execution profiles, review history, and machine
operations features. Its draft research-steward concept is relevant, but its
issue/PR publication flow should not be imposed on this repository, where research
uses commits and findings reviews rather than PRs.

Once the nightly loop works, decide whether to expose its status, reports,
backlog, and model settings as a research view in ptc manager. Reuse proven
components where practical; avoid two competing queues or copies of research
records. No separate research-manager application is required for the first
version.

## Implementation milestones

1. **Agree the operating policy.** Select one research program, its approved
   backlog, limits, model roles, and report destination.
2. **Complete one manual coordinator cycle.** Reuse the current runner and
   records, with explicit handoffs between preparation, execution, validation,
   review, and reporting.
3. **Automate and schedule that cycle on the Mini.** Add resumable coordinator
   state, configured reviewer invocation, and completion/failure notifications.
4. **Run several nights from the approved backlog.** Verify recovery from
   interruption, missing outputs, model unavailability, and review findings.
5. **Expand autonomy and presentation.** Only then add bounded new-experiment
   creation, an HTML/blog view, interactive charts, or ptc manager integration.

The first version is successful when a selected approved experiment completes
overnight, produces validated results and a reviewed illustrated morning report,
and leaves enough context to discuss the outcome and select the next experiment
without manually reconstructing the run.

## Decisions still open

- Which research program should be the first unattended pilot?
- What nightly execution and model-usage budgets should apply?
- Which actual models or agents should fill the review and advice roles?
- Where should the morning briefing be read: repository Markdown, a private HTML
  page, or a later ptc manager view?
- At what point should newly proposed experiments become eligible for automatic
  execution?

This document is an orchestration plan, not a pre-registration of any scientific
experiment and not authorization to activate a recurring run.
