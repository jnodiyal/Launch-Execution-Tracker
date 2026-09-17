# Cross-Functional Launch Execution Tracker
### A simulated Associate Program Manager workflow: process rollout, RACI ownership, and blocker-driven schedule recovery

## Business Problem

A company is rolling out a new **cycle-count (inventory audit) process** across 5 regional
warehouses. The rollout touches four functions — **Operations** (warehouse floor execution),
**Supply Chain** (data reconciliation), **Category** (SKU classification), and **Central**
(IT systems + Finance sign-off) — with no single team owning end-to-end delivery.

This is exactly the kind of initiative an Associate Program Manager is dropped into: nobody
owns the whole thing, the plan touches teams that don't normally coordinate, and the first
draft schedule is usually wrong until someone stress-tests the dependencies.

This project simulates that ownership: a task plan, a RACI matrix to fix accountability, a
schedule stress-test to remove a costly planning mistake, and a blocker log to show how a
real risk was escalated and worked around — followed by an execution tracker that flags
what's actually at risk *today*.

## What's in this repo

| File | Purpose |
|---|---|
| `data/tasks.csv` | The 15-task rollout plan, with **two** dependency structures (naive and optimized) and live progress data |
| `data/blocker_risk_log.csv` | 3 real blockers/risks raised during execution, with resolution actions |
| `launch_tracker.py` | Computes critical path (naive vs. optimized), current RAG status per task, and renders a Gantt chart |
| `build_raci.py` | Generates `RACI_Matrix.xlsx` — Responsible/Accountable/Consulted/Informed ownership per task |
| `build_blocker_log.py` | Generates `Blocker_Risk_Log.xlsx` — formatted version of the blocker log |
| `output/` | All generated reports and charts (regenerate anytime by re-running the scripts) |

## Approach

**1. Found a planning mistake before it cost time.**
The first draft schedule ran the 5 regional rollouts sequentially, one after another, because
that's how they were listed on a slide. But each region has its own floor team with no shared
equipment dependency — there was no real reason they couldn't run in parallel. Modeling both
versions as dependency graphs and computing the critical path (longest path through the task
network) quantified the mistake precisely, rather than just asserting "let's parallelize."

**2. Fixed accountability with a RACI matrix.**
Cross-functional work stalls when it's unclear who actually owns a decision vs. who just
needs to be kept in the loop. The RACI matrix (`RACI_Matrix.xlsx`) assigns exactly one
Accountable owner per task and makes Responsible/Consulted/Informed explicit for the other
three functions — so "who do I chase" is never a question during execution.

**3. Tracked blockers as they happened, not after.**
A vendor delay on the IT/WMS configuration task (T3) is logged in `blocker_risk_log.csv`
with its downstream impact, owner, and the actual resolution action taken (an interim
manual-entry workaround, negotiated with the vendor's account manager) rather than just a
"delayed" flag.

**4. Built a tracker that surfaces risk automatically.**
`launch_tracker.py` doesn't just store the plan — it computes, from today's date and current
% complete, which tasks are Green / Amber / Red, and renders that against the timeline as a
Gantt chart. This is the mechanism, not just the artifact.

## Results

Running `launch_tracker.py` against the current data:

- **Naive plan:** 48 working days end-to-end
- **Optimized plan:** 27 working days
- **Timeline reduction: 43.8%** — purely from removing one false sequential dependency
- **Current status:** the T3 vendor delay has cascaded into 9 of 15 tasks showing Red,
  which is precisely why it was escalated in the blocker log rather than left to resolve
  itself — the tracker makes that cascade visible immediately instead of surfacing it only
  once a downstream region actually misses its date.

See `output/critical_path_report.md` and `output/status_report.md` for the full breakdown,
and `output/gantt_chart.png` for the visual timeline.

## How to run it

```bash
pip install -r requirements.txt
python launch_tracker.py      # critical path + RAG status + Gantt chart
python build_raci.py          # RACI_Matrix.xlsx
python build_blocker_log.py   # Blocker_Risk_Log.xlsx
```

All outputs are written to `output/`.

## Why this project

Most student portfolios show analytical output (a dashboard, a model). This one is built
around the part of program management that's harder to show on a resume: catching a bad
plan before it costs 16 days, keeping four functions accountable to a single owner per task,
and turning a vendor delay into a logged, escalated, resolved item instead of a silent slip.
