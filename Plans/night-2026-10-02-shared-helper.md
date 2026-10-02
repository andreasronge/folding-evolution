# Night hand-off, 2026-10-02: shared-helper stages 1–3, unattended on the Mini

You are a coding agent on the Mac Mini, started automatically at 23:00 Stockholm time by
`scripts/night_agent.sh`. Nobody is awake. You have until **08:00** (9 hours); an outer watchdog
kills the session then. Work through this file from top to bottom.

The science is specified in [shared-helper-reuse.md](shared-helper-reuse.md). This file adds the
schedule, the gates, and the rules for working unattended. Where the two disagree, this file
wins on *process* and that file wins on *science*.

## What to deliver by 08:00

1. Stage 1 (Express) and stage 2 (Preserve): code, tests, results.
2. Stage 3 (Retain): code, tests, a launched and finished queue — or a clear statement of why it
   was not launched.
3. Morning half: validated results, plots, notebook §29, a one-page briefing.

Partial delivery is fine. An honest "stage 3 not launched, here is where it stands" is a good
outcome; a rushed stage 3 with unchecked code is not.

## Rules for working unattended

- **First action:** `git fetch && git merge --ff-only @{u}` (the launcher has already tried
  this), then read `CLAUDE.md`, `Plans/shared-helper-reuse.md`
  and the files it lists under "Read first".
- **State file:** keep `experiments/output/2026-10-02/s29_night/STATE.md` up to date: one line
  per phase (pending / running / done / skipped + reason), the time, and the current commit.
  Write it before and after every phase. If you are started and it already exists, resume from
  it; never launch a queue entry that `queue_s29.status.json` marks done or that is running
  (check the lock file and `ps`).
- **Never ask the human a question and wait.** Decide with the rules here. If they don't cover
  it, or you are stuck, ask Fable (next section). If that is unavailable, take the more
  conservative option, record the decision in STATE.md, and continue with whatever does not
  depend on it.
- **Do not change scientific settings to make something finish or pass.** The only allowed
  scaling is the one in "Stage 3 budget" below. Record any scaling you apply.
- **Git:** commit to `main` and push (the repo's convention). Stage only files you created or
  changed for this work, by path. Do not touch, stage or revert pre-existing uncommitted files
  (`.gitignore`, `AGENTS.md`, `queue_*.status.json`, other plans). No force-push, no history
  rewriting, no `git clean`, no `git reset --hard`.
- **Scope of changes:** new files under `experiments/chem_tape/`, `tests/`,
  `experiments/chem_tape/sweeps/mapbias/`, `docs/map-bias/notebook.md` (append §29 only),
  `docs/map-bias/figures/`. Changes in `src/folding_evolution/chem_tape/` only where stage 3
  needs them, behind options whose defaults leave existing behaviour byte-identical.
  **Do not edit `docs/map-bias/findings.md`.**
- **Machine:** at most 10 workers; one queue at a time; no installs beyond `uv sync`; do not
  delete anything under `experiments/output/` from earlier dates.
- **Failures:** diagnose before retrying; at most one retry of a failed queue entry, and only
  after you can name the cause. Keep partial rows. A post-launch code repair must keep the
  original rows and record provenance, as in notebook §28.

## Asking Fable when stuck

Fable wrote both plans and is the adviser for this night. Ask when:
- you have spent about 20 minutes on one obstacle without progress;
- a gate or a rule in either plan is ambiguous for the case in front of you;
- a check fails and you cannot name the cause;
- a result looks wrong or surprising enough that it changes what should run next.

How, from the repo root (a fresh headless session; it can read the repository but give it the
paths that matter and say what you already tried):

```
claude -p --model claude-fable-5-1 "You are advising the agent running \
Plans/night-2026-10-02-shared-helper.md unattended. Read that plan and \
Plans/shared-helper-reuse.md. <situation, file paths, what was tried, the options you see>. \
Give one recommendation and the reason. Do not edit files."
```

- At most 6 calls for the night, each with a 10-minute timeout. Do not ask for routine coding
  help or for permission to continue.
- Record each question, the answer and what you did in STATE.md.
- Fable's answer is advice. It cannot override the rules in this file: the scaling order, the
  03:30 launch deadline, the scope of changes, the git rules, no edits to `findings.md`. If the
  advice conflicts with them, follow this file and note the conflict in the briefing.
- If the command fails or the model is unavailable, say so in STATE.md and take the more
  conservative option. Do not present another model's answer as Fable's.

## Schedule and gates

All times are local. The deadlines are latest times; move on earlier if a phase is done.

| time | phase | gate to pass before moving on |
|---|---|---|
| 23:00–01:00 | A. Stage 1 + stage 2 | hand-built forms verified by test; stage 2 table written |
| 01:00–03:30 | B. Stage 3 code, checks, review, commit | all "Checks before launch" pass |
| **03:30** | launch deadline | not launched by 03:30 → skip stage 3 runs, go to D |
| 03:30–07:00 | C. Stage 3 queue runs | queue finished or timed out by 07:00 |
| 07:00–07:50 | D. Validate, plot, notebook §29, briefing, push | |
| 07:50 | final commit and push; STATE.md says finished | |

### Phase A — stages 1 and 2 (no evolution)

As specified in shared-helper-reuse.md, in `experiments/chem_tape/shared_helper.py` with tests in
`tests/test_shared_helper.py`:
- the three hand-built forms (shared, partly shared, duplicated) at each tape length they fit;
- multi-output evaluation on all 10,000 lists and the knockout measure, both tested on the
  hand-built forms (expected consumer counts are in the plan);
- stage 2 variation trials, written to `$RUN_DIR/preserve.json` and a Markdown table.

**Gate A (the plan's stop rule):** if no shared form can be written under leftmost-wins with
the `tagged` alphabet, stop the science here. Write what blocked it in the notebook, skip
phases B and C, and go to D. Do not switch join rule or alphabet to get past this.

If the cell counts differ from the plan's estimate (about 24 shared, 33 duplicated), choose the
three tape lengths so that the smallest fits only the shared form and record the choice.

Commit and push when phase A's tests pass.

### Phase B — stage 3 code and checks

Implement what the plan lists under stage 3. Then, before launch, do all of these and record
each result in STATE.md:

1. `uv run pytest` on the new tests and the existing chem-tape tagged tests.
2. **Replay:** 3 seeds of `xover_v2_xor_leftmost.yaml` give the same champions as the stored
   §25 results (defaults unchanged).
3. **Seeding:** a seeded initial population contains exactly the intended genomes; a seed-mixed
   population is half and half.
4. **Generation-0 sanity:** in a seed-shared run, generation 0 is 100% fully exact and 100%
   "shared" by knockout; in seed-dup, 100% "duplicated".
5. **Pilot:** 2 seeds per arm, full length; read the logged census; measure wall-clock.
6. **Queue validation:** `scripts/run_queue.py --validate` on `queue_s29.yaml`.
7. **Codex code review** of the stage 3 changes (`codex review` against the last commit before
   phase B, or the `/codex review` skill). One round, plus one re-review if you fixed a P1. Fix
   anything that would invalidate the night; note the rest in STATE.md. If Codex is not
   installed or fails, use a fresh `claude -p` session as reviewer instead and record that the
   review was not by Codex.
8. Commit and push. The queue runs from that commit with a clean tree for the files it uses.

**Gate B:** every check passes and it is before 03:30. Otherwise do not launch.

### Stage 3 budget

The queue must be finished by 07:00. Order the entries so the most informative run first:

1. seed-mixed at the two roomy tape lengths (the main readout);
2. seed-shared at all three lengths;
3. seed-dup at the two roomy lengths.

From the pilot, estimate the total. If it does not fit between launch and 07:00, scale in this
order and no other: (a) drop seed-dup; (b) 30 → 20 seeds in every remaining arm; (c) 1000 → 500
generations in every remaining arm. If entry 1 alone does not fit after (b) and (c), do not
launch. Set each entry's timeout so the whole queue ends by 07:00. Record what was scaled.

Launch as in earlier nights, for example:

```
nohup caffeinate -s uv run python scripts/run_queue.py \
  --queue experiments/chem_tape/sweeps/mapbias/queue_s29.yaml \
  --status experiments/chem_tape/sweeps/mapbias/queue_s29.status.json \
  --lock experiments/chem_tape/sweeps/mapbias/queue_s29.lock \
  > experiments/output/queue_s29.log 2>&1 &
```

Confirm the first entry is producing rows. While it runs, check every 20–30 minutes; use the
waiting time to write the analysis and plotting code against the pilot output.

### Phase D — morning half

Do this at 07:00 whatever state the queue is in.

1. **Validate:** expected arms, seeds and tape lengths present; no duplicate run keys; the
   execution commit and clean-tree flag in each run's metadata; exit codes. An exit code of zero
   is not enough. Count nothing missing as a result; say PARTIAL where rows are missing.
2. **Analyse** with actual denominators. The readouts are the four listed in the plan's stage 3.
3. **Inspect** at least five final fully exact genomes per arm by eye (decode the runs): do the
   knockout labels match what the genome visibly does? Report any surprise or shortcut.
4. **Plots** in `docs/map-bias/figures/`: shared fraction among fully exact individuals over
   generations in seed-mixed, one line per tape length with the per-seed spread; and the stage 2
   survival table as a bar chart (shared vs duplicated, per operator).
5. **Notebook §29** appended to `docs/map-bias/notebook.md`: one paragraph before, plain results
   after, the commits, what was scaled or skipped, and the stage 1–3 tables. Plain language; say
   what was observed, then what it does and does not show. Mark it "Fable review pending".
6. **Briefing** at `experiments/output/2026-10-02/s29_night/briefing.md`, one page:
   what was tested and why; what happened, with the key numbers and the plots; what it teaches
   within the tested scope; failures, missing data and doubts; and which of the plan's three
   stage-3 readings applies ("needs size pressure" / "preservation is the obstacle" /
   "discovery is the obstacle"), with at most three suggested next steps.
7. Final commit and push. Last line of STATE.md: `finished <time>, commit <hash>`.

## How this session is started (for the human)

On the Mini, inside a persistent session (Herdr, tmux, or similar), from the repo root:

```
git fetch && git merge --ff-only @{u}
AGENT_CMD='<your headless agent command>' scripts/night_agent.sh \
  --at 23:00 --max-hours 9 Plans/night-2026-10-02-shared-helper.md
```

`AGENT_CMD` is the command that runs an agent non-interactively with a prompt as its last
argument and with permission to edit files, run commands, commit and push without asking.
The script waits until 23:00, keeps the machine awake, passes a short kickoff prompt naming
this file, enforces the 9-hour limit, and logs to `experiments/output/night_agent_<date>.log`.
Running the same command again later resumes from STATE.md.
