# Night s29 state (Plans/night-2026-10-02-shared-helper.md)

Started 2026-10-02 12:59 (prompt pasted early, ~13:00; plan deadlines unchanged). Start commit fa36ac7.

| phase | status | time | commit | note |
|---|---|---|---|---|
| A. stage 1+2 | done | 13:07 | 9848d08 | Gate A passed: shared form expressible (24 cells). Tests 13/13. stage1/express.md, stage2/preserve.{json,md} (77 cells x 10,000) |
| B. stage 3 code+checks | done | 13:39 | 7141ecf | all checks B1-B8 passed; 2 Codex reviews, 2 P2 fixed, no P1 |
| C. stage 3 queue | done | 14:35 | 7141ecf | 3/3 entries done, exit 0; wall 1030 / 1319 / 1024 s; no scaling |
| D. morning half | done | 14:40 | 441be87 | validated 210/210, report/s29_report.md, 2 figures, notebook §29, briefing.md |

## Fable calls (0/6)

## Decisions / notes
- 13:03 Stored §25 run outputs (2026-09-29) are not on this machine. Replay check B2 will instead compare 3 seeds (0-2, both paired arms) of xover_v2_xor_leftmost.yaml run at fa36ac7 (before any change; output replay/base_fa36ac7) against the same configs after the stage 3 changes. Conservative substitute; same intent (defaults unchanged).
- Cell counts match the plan (24 shared, 27 partly, 33 duplicated), so tape lengths stay 32/64/128. Note: partly shared (27) also fits at 32; only duplicated is excluded there.
- Stage 2 'other form' pairing: shared<->duplicated, partly->shared; skipped where the other form does not fit (shared at 32).
- Stage 2 observation: mutation survival falls with L for every form because trailing NOP padding belongs to the last run (tag 2), so insertions there change output 2.
- 13:26 B1 pytest: tests/ 869 passed (incl. 13 stage-1 + 18 stage-3 tests). PASS
- 13:26 B2 replay: 3 seeds x 2 paired arms of xover_v2_xor_leftmost.yaml at working tree vs fa36ac7 baseline: same hashes, identical result.json (minus elapsed) and final_population.npz for all 6. PASS
- 13:26 B3/B4 seeding + gen-0 sanity: covered by tests (exact 50/50 split; gen-0 census 100% fully exact, 100% shared / 100% duplicated / ~50:50 mixed); to be re-read in pilot output.
- 13:26 Pilot launched (2 seeds/arm, 1000 gens, 14 runs, 10 workers). Codex review round 1 launched (codex_review_1.txt).
- 13:30 B7 Codex review 1 (codex_review_1.txt; first attempt with a custom prompt was rejected by the CLI, rerun as plain 'codex review --uncommitted'): one P2, no P1. P2: genome_outputs(out_tags=...) shared the run memo across outputs, so with output runs reading each other in a cycle a later output reused a value from another recursion context. Fixed: fresh memo per output (same semantics as single-output OUTPUT_TAG); stage-1 shared_helper.outputs now uses the same path. Test added. Stage 1 and stage 2 re-run: identical tables (old output kept as stage1_before_memo_fix/, stage2_before_memo_fix/).
- 13:30 B5 pilot 1 (pre-fix code; kept in pilot/): 14 runs, wall 282 s, 86-175 s per run. Gen-0 census: fully exact 1.0 in all; shared 1.0 (seed-shared), duplicated 1.0 (seed-dup), 0.46-0.52 shared (seed-mixed). Final (gen 1000): fully exact ~0.30-0.42 of sample; seed-mixed -> ~99-100% shared among fully exact; seed-shared stays 100% shared; seed-dup -> ~99% PARTLY shared (tags 1,2 replace their copy of A by RECV0; checked by decoding non-elite genomes). Report-script bug found and fixed: the first fully exact individual is an elite slot (frozen original seed), so inspection now samples non-elites and reports elites separately.
- 13:30 Pilot 2 on fixed code launched (pilot2/); Codex review 2 launched (codex_review_2.txt). B6 queue validate: OK.
- 13:39 B7 Codex review 2 (codex_review_2.txt): one P2, no P1 — census/run census keep the first task's outputs under task alternation. Not used tonight; fixed by rejecting multi-output tasks / track_shared with task alternation (test added). Two reviews used (plan max).
- 13:39 B5 pilot 2 (fixed code, pilot2/): 14 runs, wall 294 s; same gen-0 census and same final pattern as pilot 1. Estimate for the full queue: 210 runs x ~140 s / 10 workers ~ 50 min. No scaling needed.
- 13:39 B8 committed + pushed 7141ecf. Replay re-run on the committed clean tree: identical to fa36ac7 baseline (6/6). Gate B passed.
- 13:39 Queue launched (detached: python Popen start_new_session; nohup/screen failed in this environment). Log experiments/output/queue_s29.log.
- 13:39 Entry metadata says git_dirty=true: the only untracked files are the runner's own queue_s29.lock and queue_s29.status.json (git status --porcelain checked at launch+1 min). Code tree clean at 7141ecf.
- 13:41 First entry producing rows (5 result.json by 13:41).
- 13:56 Entry 1 seed-mixed done (60 results); entry 2 running.
- 14:09 User (present): heavy experiments preferably 23:00-08:00. Asked; user chose to let this queue finish now. No further heavy runs before 23:00.
finished 14:40, commit 441be87
