"""
Builds RACI_Matrix.xlsx — Responsible / Accountable / Consulted / Informed
matrix mapping each task to the four functions involved in the rollout.
"""
import os
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FUNCTIONS = ["Program Lead", "Operations", "Supply Chain", "Category", "Central (IT)", "Central (Finance)"]

# task_id -> {function: role_letter}
RACI = {
    "T1":  {"Program Lead": "A/R", "Operations": "C", "Supply Chain": "C", "Category": "C", "Central (IT)": "I", "Central (Finance)": "I"},
    "T2":  {"Program Lead": "A", "Central (Finance)": "R", "Operations": "I", "Supply Chain": "I", "Category": "I", "Central (IT)": "I"},
    "T3":  {"Program Lead": "A", "Central (IT)": "R", "Operations": "I", "Supply Chain": "I", "Category": "I", "Central (Finance)": "I"},
    "T4":  {"Program Lead": "A", "Category": "R", "Operations": "C", "Supply Chain": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T5":  {"Program Lead": "A", "Operations": "R", "Category": "C", "Supply Chain": "I", "Central (IT)": "C", "Central (Finance)": "I"},
    "T6":  {"Program Lead": "A", "Operations": "R", "Supply Chain": "I", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T7":  {"Program Lead": "A", "Operations": "R", "Supply Chain": "I", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T8":  {"Program Lead": "A", "Operations": "R", "Supply Chain": "I", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T9":  {"Program Lead": "A", "Operations": "R", "Supply Chain": "I", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T10": {"Program Lead": "A", "Operations": "R", "Supply Chain": "I", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T11": {"Program Lead": "A", "Supply Chain": "R", "Operations": "C", "Category": "I", "Central (IT)": "I", "Central (Finance)": "I"},
    "T12": {"Program Lead": "A", "Supply Chain": "R", "Central (Finance)": "C", "Operations": "I", "Category": "I", "Central (IT)": "I"},
    "T13": {"Program Lead": "A", "Central (Finance)": "R", "Supply Chain": "C", "Operations": "I", "Category": "I", "Central (IT)": "I"},
    "T14": {"Program Lead": "A", "Category": "R", "Operations": "C", "Supply Chain": "C", "Central (IT)": "I", "Central (Finance)": "I"},
    "T15": {"Program Lead": "A/R", "Operations": "C", "Supply Chain": "C", "Category": "C", "Central (IT)": "C", "Central (Finance)": "C"},
}

ROLE_COLORS = {
    "R": "C8E6C9",     # green
    "A": "BBDEFB",     # blue
    "A/R": "90CAF9",   # darker blue
    "C": "FFF9C4",     # yellow
    "I": "ECEFF1",     # grey
}


def load_task_names():
    names = {}
    with open(os.path.join(DATA_DIR, "tasks.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names[row["Task_ID"]] = row["Task_Name"]
    return names


def build():
    task_names = load_task_names()
    wb = Workbook()
    ws = wb.active
    ws.title = "RACI Matrix"

    header_font = Font(name="Arial", bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="37474F")
    title_font = Font(name="Arial", bold=True, size=14)
    normal_font = Font(name="Arial", size=10)
    thin = Side(style="thin", color="B0BEC5")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    ws["A1"] = "Cycle-Count Process Rollout — RACI Matrix"
    ws["A1"].font = title_font
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2 + len(FUNCTIONS))

    ws["A2"] = "R = Responsible   A = Accountable   C = Consulted   I = Informed"
    ws["A2"].font = Font(name="Arial", italic=True, size=9)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=2 + len(FUNCTIONS))

    header_row = 4
    ws.cell(row=header_row, column=1, value="Task ID").font = header_font
    ws.cell(row=header_row, column=2, value="Task Name").font = header_font
    for c in (1, 2):
        ws.cell(row=header_row, column=c).fill = header_fill
        ws.cell(row=header_row, column=c).alignment = center
        ws.cell(row=header_row, column=c).border = border

    for i, fn in enumerate(FUNCTIONS, start=3):
        cell = ws.cell(row=header_row, column=i, value=fn)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    r = header_row + 1
    for tid, mapping in RACI.items():
        ws.cell(row=r, column=1, value=tid).font = normal_font
        ws.cell(row=r, column=1).alignment = center
        ws.cell(row=r, column=1).border = border

        ws.cell(row=r, column=2, value=task_names[tid]).font = normal_font
        ws.cell(row=r, column=2).alignment = left
        ws.cell(row=r, column=2).border = border

        for i, fn in enumerate(FUNCTIONS, start=3):
            role = mapping.get(fn, "")
            cell = ws.cell(row=r, column=i, value=role)
            cell.alignment = center
            cell.font = normal_font
            cell.border = border
            if role in ROLE_COLORS:
                cell.fill = PatternFill("solid", fgColor=ROLE_COLORS[role])
        r += 1

    ws.column_dimensions["A"].width = 9
    ws.column_dimensions["B"].width = 38
    for i in range(3, 3 + len(FUNCTIONS)):
        ws.column_dimensions[get_column_letter(i)].width = 15

    ws.freeze_panes = "C5"

    out_path = os.path.join(OUTPUT_DIR, "RACI_Matrix.xlsx")
    wb.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    build()
