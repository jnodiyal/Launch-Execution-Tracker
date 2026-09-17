"""
Launch Execution Tracker
-------------------------
Simulates an Associate Program Manager's core toolkit for a cross-functional
process rollout: critical-path scheduling, RAG (Red/Amber/Green) status
tracking, and blocker-aware timeline visualization.

Scenario: Rolling out a new cycle-count (inventory audit) process across
5 regional warehouses, coordinated across Operations, Supply Chain,
Category, and Central (IT/Finance) functions.

Usage:
    python launch_tracker.py

Outputs (written to ./output/):
    - critical_path_report.md   : naive vs. optimized schedule comparison
    - status_report.md          : current RAG status of every task
    - gantt_chart.png           : visual timeline, optimized plan, colored by status
"""

import os
import csv
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
PROJECT_START = date(2026, 8, 24)   # day the rollout kicked off
SNAPSHOT_DATE = date(2026, 9, 17)   # "today" - when this status report is run

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_tasks():
    tasks = {}
    with open(os.path.join(DATA_DIR, "tasks.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tasks[row["Task_ID"]] = {
                "name": row["Task_Name"],
                "function": row["Function"],
                "owner": row["Owner_Role"],
                "duration": int(row["Duration_Days"]),
                "deps_naive": [d for d in row["Dependencies_Naive"].split(",") if d],
                "deps_opt": [d for d in row["Dependencies_Optimized"].split(",") if d],
                "pct_complete": int(row["Percent_Complete"]),
                "status": row["Status"],
            }
    return tasks


def longest_path_schedule(tasks, dep_key):
    """
    Forward-pass critical path calculation (earliest start/finish) over a DAG.
    Returns dict of task_id -> (earliest_start_day, earliest_finish_day),
    where day 0 = project start.
    """
    finish = {}

    def compute_finish(tid, visiting=None):
        if tid in finish:
            return finish[tid]
        visiting = visiting or set()
        if tid in visiting:
            raise ValueError(f"Circular dependency detected at {tid}")
        visiting.add(tid)
        deps = tasks[tid][dep_key]
        earliest_start = 0
        for d in deps:
            _, dep_finish = compute_finish(d, visiting)
            earliest_start = max(earliest_start, dep_finish)
        f = earliest_start + tasks[tid]["duration"]
        finish[tid] = (earliest_start, f)
        return finish[tid]

    for tid in tasks:
        compute_finish(tid)
    return finish


def critical_path_report(tasks):
    naive = longest_path_schedule(tasks, "deps_naive")
    optimized = longest_path_schedule(tasks, "deps_opt")

    naive_total = max(f for _, f in naive.values())
    opt_total = max(f for _, f in optimized.values())
    days_saved = naive_total - opt_total
    pct_reduction = round(100 * days_saved / naive_total, 1)

    lines = []
    lines.append("# Critical Path: Naive vs. Optimized Schedule\n")
    lines.append(f"- **Naive (fully sequential) plan total duration:** {naive_total} working days")
    lines.append(f"- **Optimized (parallelized) plan total duration:** {opt_total} working days")
    lines.append(f"- **Timeline reduction:** {days_saved} days saved ({pct_reduction}% shorter)\n")
    lines.append(
        "The naive plan ran the 5 regional rollouts (T6-T10) one after another. "
        "Since each region has an independent floor team with no shared equipment "
        "dependency, they can execute in parallel once training (T5) is complete. "
        "Resequencing the plan around this single false dependency accounts for "
        "nearly all of the time saved.\n"
    )
    lines.append("| Task | Naive Finish (day) | Optimized Finish (day) |")
    lines.append("|---|---|---|")
    for tid in tasks:
        lines.append(f"| {tid}: {tasks[tid]['name']} | {naive[tid][1]} | {optimized[tid][1]} |")

    with open(os.path.join(OUTPUT_DIR, "critical_path_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return optimized, naive_total, opt_total, pct_reduction


def rag_status(task, planned_finish_day):
    """Classify a task as Green/Amber/Red based on progress vs. planned finish."""
    planned_finish_date = PROJECT_START + timedelta(days=planned_finish_day)
    days_remaining = (planned_finish_date - SNAPSHOT_DATE).days

    if task["status"] == "Complete":
        return "Green"
    if task["status"] == "Not Started" and days_remaining < 0:
        return "Red"
    if task["pct_complete"] == 0 and days_remaining <= 3:
        return "Amber"
    if days_remaining < 0 and task["pct_complete"] < 100:
        return "Red"
    if 0 < days_remaining <= 2 and task["pct_complete"] < 80:
        return "Amber"
    return "Green"


def status_report(tasks, optimized_schedule):
    lines = ["# Current Status Report", f"_Snapshot date: {SNAPSHOT_DATE.isoformat()}_\n"]
    lines.append("| Task | Function | % Complete | Status | Planned Finish | RAG |")
    lines.append("|---|---|---|---|---|---|")

    rag_counts = {"Green": 0, "Amber": 0, "Red": 0}
    for tid, t in tasks.items():
        _, finish_day = optimized_schedule[tid]
        planned_finish = PROJECT_START + timedelta(days=finish_day)
        rag = rag_status(t, finish_day)
        rag_counts[rag] += 1
        lines.append(
            f"| {tid}: {t['name']} | {t['function']} | {t['pct_complete']}% | "
            f"{t['status']} | {planned_finish.isoformat()} | {rag} |"
        )

    lines.append(f"\n**Summary:** {rag_counts['Green']} Green, {rag_counts['Amber']} Amber, {rag_counts['Red']} Red\n")

    with open(os.path.join(OUTPUT_DIR, "status_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return rag_counts


def gantt_chart(tasks, optimized_schedule):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    color_map = {"Complete": "#2E7D32", "In Progress": "#F9A825", "Not Started": "#B0BEC5"}

    ordered_ids = list(tasks.keys())
    fig, ax = plt.subplots(figsize=(11, 6.5))

    for i, tid in enumerate(reversed(ordered_ids)):
        start, finish = optimized_schedule[tid]
        duration = finish - start
        color = color_map.get(tasks[tid]["status"], "#B0BEC5")
        ax.barh(i, duration, left=start, height=0.6, color=color, edgecolor="black", linewidth=0.5)
        ax.text(start + duration / 2, i, tid, ha="center", va="center", fontsize=8, color="white" if color != "#B0BEC5" else "black")

    ax.set_yticks(range(len(ordered_ids)))
    ax.set_yticklabels([tasks[tid]["name"] for tid in reversed(ordered_ids)], fontsize=8)
    ax.set_xlabel("Project Day (0 = start, {})".format(PROJECT_START.isoformat()))
    ax.set_title("Cycle-Count Process Rollout — Optimized Timeline")

    # snapshot line
    snapshot_day = (SNAPSHOT_DATE - PROJECT_START).days
    ax.axvline(snapshot_day, color="crimson", linestyle="--", linewidth=1.2)
    ax.text(snapshot_day + 0.3, len(ordered_ids) - 0.5, "Today", color="crimson", fontsize=8)

    legend_handles = [mpatches.Patch(color=c, label=s) for s, c in color_map.items()]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "gantt_chart.png"), dpi=150)
    plt.close()


def main():
    tasks = load_tasks()
    optimized_schedule, naive_total, opt_total, pct_reduction = critical_path_report(tasks)
    rag_counts = status_report(tasks, optimized_schedule)
    gantt_chart(tasks, optimized_schedule)

    print("Launch Execution Tracker — Summary")
    print("=" * 40)
    print(f"Naive plan duration:     {naive_total} days")
    print(f"Optimized plan duration: {opt_total} days")
    print(f"Timeline reduction:      {pct_reduction}%")
    print(f"Current RAG status:      {rag_counts}")
    print(f"\nReports written to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
