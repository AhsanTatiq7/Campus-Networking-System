import customtkinter as ctk
from tkinter import messagebox
from collections import deque
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")

# =========================================
# APP SETTINGS
# =========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================================
# COLOR PALETTE
# =========================================
ACCENT       = "#00D4FF"
ACCENT2      = "#7C3AED"
SUCCESS      = "#10B981"
WARNING      = "#F59E0B"
DANGER       = "#EF4444"
BG_DARK      = "#0A0E1A"
BG_CARD      = "#111827"
BG_SIDEBAR   = "#0D1117"
BG_INNER     = "#1A2235"
BG_TAG       = "#1E2D45"
BORDER       = "#1F2937"
TEXT_PRIMARY = "#F9FAFB"
TEXT_MUTED   = "#6B7280"

DEPT_COLORS = {
    "CS":  "#00D4FF", "AI":  "#7C3AED", "SE":  "#10B981",
    "EE":  "#F59E0B", "ME":  "#EF4444", "BBA": "#EC4899",
    "DS":  "#06B6D4", "IT":  "#84CC16",
}
DEPT_BG = {
    "CS":  "#0A2A33", "AI":  "#1A0F33", "SE":  "#0A2018",
    "EE":  "#2D1F00", "ME":  "#2D0A0A", "BBA": "#2D0A1A",
    "DS":  "#051E22", "IT":  "#141F00",
}

def dept_color(dept):
    return DEPT_COLORS.get(dept.upper().strip(), TEXT_MUTED)

def dept_bg_color(dept):
    return DEPT_BG.get(dept.upper().strip(), BG_INNER)

def get_initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if len(name) >= 2 else name.upper()

# =========================================
# DATA
# =========================================
network = {}
departments = {}
interests = {}

def save_data():
    with open("students.txt", "w") as f:
        for s in network:
            f.write(f"{s}|{departments.get(s,'')}|"
                    f"{','.join(interests.get(s,[]))}|"
                    f"{','.join(network.get(s,[]))}\n")

def load_data():
    if not os.path.exists("students.txt"):
        return
    with open("students.txt", "r") as f:
        for line in f:
            d = line.strip().split("|")
            if len(d) < 4:
                continue
            name = d[0]
            network[name]     = [x for x in d[3].split(",") if x]
            departments[name] = d[1]
            interests[name]   = [x for x in d[2].split(",") if x]

# =========================================
# POPUP / WIDGET HELPERS
# =========================================
def make_popup(title_text, width=460, height=420):
    win = ctk.CTkToplevel(app)
    win.title(title_text)
    win.geometry(f"{width}x{height}")
    win.configure(fg_color=BG_CARD)
    win.grab_set()
    ctk.CTkFrame(win, height=4, fg_color=ACCENT,
                 corner_radius=0).pack(fill="x")
    ctk.CTkLabel(win, text=title_text,
                 font=("Arial", 18, "bold"),
                 text_color=ACCENT).pack(pady=(18, 8))
    ctk.CTkFrame(win, height=1, fg_color=BORDER,
                 corner_radius=0).pack(fill="x", padx=30, pady=(0, 12))
    return win

def make_entry(parent, placeholder, width=300):
    return ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        width=width, height=40, corner_radius=8,
        border_color=BORDER, fg_color=BG_INNER,
        text_color=TEXT_PRIMARY,
        placeholder_text_color=TEXT_MUTED,
        font=("Arial", 13)
    )

def make_btn(parent, text, cmd, color=ACCENT2, hover=ACCENT, width=210):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        width=width, height=40, corner_radius=8,
        fg_color=color, hover_color=hover,
        text_color="white", font=("Arial", 14, "bold")
    )

# =========================================
# CONFIRM DIALOG
# =========================================
def confirm_dialog(title, message, confirm_text="Delete", confirm_color=DANGER):
    result = [False]
    dlg = ctk.CTkToplevel(app)
    dlg.title(title)
    dlg.geometry("400x230")
    dlg.configure(fg_color=BG_CARD)
    dlg.grab_set()
    dlg.resizable(False, False)
    ctk.CTkFrame(dlg, height=4, fg_color=confirm_color,
                 corner_radius=0).pack(fill="x")
    ctk.CTkLabel(dlg, text=f"⚠  {title}",
                 font=("Arial", 16, "bold"),
                 text_color=confirm_color).pack(pady=(20, 6))
    ctk.CTkLabel(dlg, text=message,
                 font=("Arial", 12), text_color=TEXT_PRIMARY,
                 wraplength=340, justify="center").pack(pady=(0, 20))
    br = ctk.CTkFrame(dlg, fg_color="transparent")
    br.pack(pady=4)
    ctk.CTkButton(br, text="Cancel", width=140, height=38, corner_radius=8,
                  fg_color=BG_INNER, hover_color=BORDER,
                  text_color=TEXT_MUTED, font=("Arial", 13, "bold"),
                  command=lambda: [result.__setitem__(0, False),
                                   dlg.destroy()]).pack(side="left", padx=8)
    ctk.CTkButton(br, text=confirm_text, width=140, height=38, corner_radius=8,
                  fg_color=confirm_color,
                  hover_color="#B91C1C" if confirm_color == DANGER else confirm_color,
                  text_color="white", font=("Arial", 13, "bold"),
                  command=lambda: [result.__setitem__(0, True),
                                   dlg.destroy()]).pack(side="left", padx=8)
    dlg.wait_window()
    return result[0]

# =========================================
# TOAST
# =========================================
_toast_after = None

def show_toast(msg, color=SUCCESS):
    global _toast_after
    toast_lbl.configure(text=f"  {msg}  ")
    toast_frame.configure(fg_color=color)
    toast_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-16, y=68)
    if _toast_after:
        app.after_cancel(_toast_after)
    _toast_after = app.after(2600, toast_frame.place_forget)

# =========================================
# OUTPUT
# =========================================
def log(text, toast=None, tc=SUCCESS):
    output_box.configure(state="normal")
    output_box.insert("end", f"  ✦  {text}\n")
    output_box.see("end")
    if toast:
        show_toast(toast, tc)

def set_out(text):
    output_box.configure(state="normal")
    output_box.delete("1.0", "end")
    output_box.insert("end", text)

def sec(title):
    bar = "─" * 44
    return f"\n  {bar}\n   {title}\n  {bar}\n\n"

# =========================================
# VIEW SWITCHER
# =========================================
def show_cards_view():
    output_area.pack_forget()
    cards_area.pack(side="left", fill="both", expand=True)
    btn_cards.configure(fg_color=ACCENT2, text_color="white")
    btn_log.configure(fg_color="transparent", text_color=TEXT_MUTED)

def show_log_view():
    cards_area.pack_forget()
    output_area.pack(side="left", fill="both",
                     expand=True, padx=20, pady=(0, 16))
    btn_log.configure(fg_color=ACCENT2, text_color="white")
    btn_cards.configure(fg_color="transparent", text_color=TEXT_MUTED)

# =========================================
# PROFILE  — full centered popup (balanced)
# =========================================
def open_profile(student):
    dept  = departments.get(student, "?")
    dc    = dept_color(dept)
    dbc   = dept_bg_color(dept)
    conns = network.get(student, [])
    tags  = interests.get(student, [])
    inits = get_initials(student)

    pw = ctk.CTkToplevel(app)
    pw.title(f"Profile — {student}")
    pw.geometry("580x560")
    pw.configure(fg_color=BG_DARK)
    pw.grab_set()
    pw.resizable(False, False)

    # top accent bar
    ctk.CTkFrame(pw, height=4, fg_color=dc, corner_radius=0).pack(fill="x")

    # ── COMPACT hero: avatar LEFT + name/dept RIGHT (not stacked)
    hero = ctk.CTkFrame(pw, fg_color=dbc, corner_radius=0)
    hero.pack(fill="x")

    hi = ctk.CTkFrame(hero, fg_color="transparent")
    hi.pack(pady=14, padx=20, anchor="w")

    av = ctk.CTkFrame(hi, width=62, height=62, corner_radius=31,
                      fg_color=BG_DARK, border_color=dc, border_width=2)
    av.pack(side="left")
    av.pack_propagate(False)
    ctk.CTkLabel(av, text=inits, font=("Arial", 20, "bold"),
                 text_color=dc).place(relx=0.5, rely=0.5, anchor="center")

    nc = ctk.CTkFrame(hi, fg_color="transparent")
    nc.pack(side="left", padx=14, anchor="w")
    ctk.CTkLabel(nc, text=student, font=("Arial", 17, "bold"),
                 text_color=TEXT_PRIMARY).pack(anchor="w")
    dp = ctk.CTkFrame(nc, fg_color=BG_DARK, corner_radius=16)
    dp.pack(anchor="w", pady=3)
    ctk.CTkLabel(dp, text=f"  {dept} Department  ",
                 font=("Arial", 10, "bold"), text_color=dc).pack(padx=2, pady=3)

    # ── 3 stat boxes inline
    sr = ctk.CTkFrame(pw, fg_color="transparent")
    sr.pack(fill="x", padx=16, pady=(10, 6))

    def sbox(parent, val, label, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=9,
                         border_color=BORDER, border_width=1)
        f.pack(side="left", expand=True, fill="x", padx=3)
        ctk.CTkLabel(f, text=str(val), font=("Arial", 18, "bold"),
                     text_color=color).pack(pady=(7, 0))
        ctk.CTkLabel(f, text=label, font=("Arial", 8),
                     text_color=TEXT_MUTED).pack(pady=(0, 7))

    sbox(sr, len(conns),       "CONNECTIONS", SUCCESS)
    sbox(sr, len(tags),        "INTERESTS",   WARNING)
    sbox(sr, len(network) - 1, "IN NETWORK",  ACCENT)

    # ── scrollable body
    body = ctk.CTkScrollableFrame(pw, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=16, pady=(2, 0))

    # interests
    ctk.CTkLabel(body, text="INTERESTS", font=("Arial", 10, "bold"),
                 text_color=TEXT_MUTED).pack(anchor="w", pady=(6, 3))
    if tags:
        tw = ctk.CTkFrame(body, fg_color="transparent")
        tw.pack(fill="x", pady=(0, 8))
        rf = None
        for i, tag in enumerate(tags):
            if i % 5 == 0:
                rf = ctk.CTkFrame(tw, fg_color="transparent")
                rf.pack(anchor="w", pady=1)
            pill = ctk.CTkFrame(rf, fg_color=BG_TAG, corner_radius=6)
            pill.pack(side="left", padx=2)
            ctk.CTkLabel(pill, text=f"  {tag}  ",
                         font=("Arial", 10), text_color=ACCENT).pack(pady=4)
    else:
        ctk.CTkLabel(body, text="No interests listed.",
                     font=("Arial", 10), text_color=TEXT_MUTED
                     ).pack(anchor="w", pady=(0, 8))

    ctk.CTkFrame(body, height=1, fg_color=BORDER,
                 corner_radius=0).pack(fill="x", pady=(0, 6))

    # connections — 2-col grid
    ch = ctk.CTkFrame(body, fg_color="transparent")
    ch.pack(fill="x", pady=(0, 4))
    ctk.CTkLabel(ch, text="CONNECTIONS", font=("Arial", 10, "bold"),
                 text_color=TEXT_MUTED).pack(side="left")
    ctk.CTkLabel(ch, text=str(len(conns)), font=("Arial", 11, "bold"),
                 text_color=SUCCESS).pack(side="right")

    if conns:
        cg = ctk.CTkFrame(body, fg_color="transparent")
        cg.pack(fill="x")
        cg.grid_columnconfigure(0, weight=1)
        cg.grid_columnconfigure(1, weight=1)
        for idx, c in enumerate(conns):
            c_dept = departments.get(c, "?")
            c_dc   = dept_color(c_dept)
            c_dbc  = dept_bg_color(c_dept)
            c_init = get_initials(c)
            shared = set(tags) & set(interests.get(c, []))

            row = ctk.CTkFrame(cg, fg_color=BG_CARD, corner_radius=8,
                               border_color=BORDER, border_width=1)
            row.grid(row=idx // 2, column=idx % 2,
                     padx=3, pady=3, sticky="ew")

            cav = ctk.CTkFrame(row, width=32, height=32,
                               corner_radius=16, fg_color=c_dbc,
                               border_color=c_dc, border_width=1)
            cav.pack(side="left", padx=(8, 6), pady=7)
            cav.pack_propagate(False)
            ctk.CTkLabel(cav, text=c_init[0], font=("Arial", 10, "bold"),
                         text_color=c_dc
                         ).place(relx=0.5, rely=0.5, anchor="center")

            inf = ctk.CTkFrame(row, fg_color="transparent")
            inf.pack(side="left", anchor="w", pady=6)
            ctk.CTkLabel(inf, text=c, font=("Arial", 11, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            if shared:
                ctk.CTkLabel(inf, text="♦ " + " · ".join(shared),
                             font=("Arial", 9),
                             text_color=WARNING).pack(anchor="w")

            b = ctk.CTkFrame(row, fg_color=c_dbc, corner_radius=5)
            b.pack(side="right", padx=7, pady=6)
            ctk.CTkLabel(b, text=f" {c_dept} ", font=("Arial", 9, "bold"),
                         text_color=c_dc).pack(pady=2)
    else:
        ctk.CTkLabel(body, text="No connections yet.",
                     font=("Arial", 11), text_color=TEXT_MUTED
                     ).pack(anchor="w", pady=6)

    ctk.CTkButton(pw, text="Close", height=34, corner_radius=8,
                  fg_color=BG_INNER, hover_color=BORDER,
                  text_color=TEXT_MUTED, font=("Arial", 12, "bold"),
                  command=pw.destroy
                  ).pack(fill="x", padx=16, pady=8)

# =========================================
# CARD GRID
# =========================================
_search_job = None

def render_cards(student_list=None, hi_student=None, hi_interest=None):
    for w in cards_grid.winfo_children():
        w.destroy()

    students = (student_list if student_list is not None
                else list(network.keys()))

    if not students:
        ef = ctk.CTkFrame(cards_grid, fg_color="transparent")
        ef.grid(row=0, column=0, columnspan=3, pady=80, padx=30)
        ctk.CTkLabel(ef, text="◈", font=("Arial", 48),
                     text_color=BORDER).pack()
        ctk.CTkLabel(ef,
                     text="No students yet" if not network
                     else "No matches found",
                     font=("Arial", 18, "bold"),
                     text_color=TEXT_MUTED).pack(pady=(8, 4))
        ctk.CTkLabel(ef,
                     text='Use "Add Student" in the sidebar to get started.'
                     if not network else "Try a different search or filter.",
                     font=("Arial", 12),
                     text_color=TEXT_MUTED).pack()
        return

    max_conns = max((len(network[s]) for s in network), default=0)
    COLS = 3
    for ci in range(COLS):
        cards_grid.grid_columnconfigure(ci, weight=1)

    for idx, name in enumerate(students):
        ri = idx // COLS
        ci = idx % COLS
        dept  = departments.get(name, "?")
        dc    = dept_color(dept)
        dbc   = dept_bg_color(dept)
        inits = get_initials(name)
        conns = network.get(name, [])
        tags  = interests.get(name, [])
        is_popular = (max_conns > 0 and len(conns) == max_conns)
        border_c = dc if name == hi_student else BORDER
        border_w = 2 if name == hi_student else 1

        card = ctk.CTkFrame(cards_grid, fg_color=BG_CARD,
                            corner_radius=12,
                            border_color=border_c, border_width=border_w)
        card.grid(row=ri, column=ci, padx=8, pady=8, sticky="nsew")

        ctk.CTkFrame(card, height=4, fg_color=dc,
                     corner_radius=0).pack(fill="x")

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(12, 0))

        av = ctk.CTkFrame(top_row, width=52, height=52,
                          corner_radius=26, fg_color=dbc,
                          border_color=dc, border_width=2)
        av.pack(side="left")
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=inits, font=("Arial", 16, "bold"),
                     text_color=dc
                     ).place(relx=0.5, rely=0.5, anchor="center")

        nc = ctk.CTkFrame(top_row, fg_color="transparent")
        nc.pack(side="left", padx=10, anchor="w")
        ctk.CTkLabel(nc, text=name, font=("Arial", 13, "bold"),
                     text_color=TEXT_PRIMARY, anchor="w",
                     wraplength=130).pack(anchor="w")
        dp = ctk.CTkFrame(nc, fg_color=dbc, corner_radius=5)
        dp.pack(anchor="w", pady=2)
        ctk.CTkLabel(dp, text=f"  {dept}  ",
                     font=("Arial", 10, "bold"),
                     text_color=dc).pack()
        if is_popular:
            pp = ctk.CTkFrame(nc, fg_color="#2D1F00", corner_radius=5)
            pp.pack(anchor="w", pady=1)
            ctk.CTkLabel(pp, text="  ★ TOP  ",
                         font=("Arial", 9, "bold"),
                         text_color=WARNING).pack()

        ctk.CTkFrame(card, height=1, fg_color=BORDER,
                     corner_radius=0).pack(fill="x", padx=12, pady=7)

        cr = ctk.CTkFrame(card, fg_color="transparent")
        cr.pack(fill="x", padx=12, pady=(0, 5))
        ctk.CTkLabel(cr, text="⟷  Connections",
                     font=("Arial", 11),
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(cr, text=str(len(conns)),
                     font=("Arial", 13, "bold"),
                     text_color=SUCCESS).pack(side="right")

        if tags:
            tr = ctk.CTkFrame(card, fg_color="transparent")
            tr.pack(fill="x", padx=10, pady=(0, 5))
            wr = ctk.CTkFrame(tr, fg_color="transparent")
            wr.pack(anchor="w")
            for tag in tags[:4]:
                tc = (WARNING if hi_interest and
                      tag.lower() == hi_interest.lower()
                      else ACCENT)
                pill = ctk.CTkFrame(wr, fg_color=BG_TAG, corner_radius=5)
                pill.pack(side="left", padx=2, pady=1)
                ctk.CTkLabel(pill, text=f" {tag} ",
                             font=("Arial", 10),
                             text_color=tc).pack()
            if len(tags) > 4:
                ctk.CTkLabel(wr, text=f"+{len(tags)-4}",
                             font=("Arial", 9),
                             text_color=TEXT_MUTED).pack(side="left", padx=3)

        # action buttons
        br = ctk.CTkFrame(card, fg_color="transparent")
        br.pack(fill="x", padx=10, pady=(2, 10))

        def on_view(n=name):  open_profile(n)
        def on_edit(n=name):  open_edit_student(n)
        def on_delete(n=name): do_delete_student(n)

        ctk.CTkButton(br, text="Profile", height=28, corner_radius=6,
                      fg_color=BG_INNER, hover_color=dbc,
                      text_color=dc, font=("Arial", 10, "bold"),
                      command=on_view
                      ).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(br, text="Edit", height=28, corner_radius=6,
                      fg_color=BG_INNER, hover_color=BG_INNER,
                      text_color=SUCCESS, font=("Arial", 10, "bold"),
                      command=on_edit
                      ).pack(side="left", expand=True, fill="x", padx=2)
        ctk.CTkButton(br, text="Delete", height=28, corner_radius=6,
                      fg_color=BG_INNER, hover_color=BG_INNER,
                      text_color=DANGER, font=("Arial", 10, "bold"),
                      command=on_delete
                      ).pack(side="left", expand=True, fill="x", padx=2)

# =========================================
# LIVE SEARCH — debounced
# =========================================
def apply_filters(*args):
    global _search_job
    if _search_job:
        app.after_cancel(_search_job)
    _search_job = app.after(180, _do_filter)

def _do_filter(*args):
    if not cards_area.winfo_ismapped():
        return
    ft   = search_var.get().strip().lower()
    dept = dept_var.get()
    result = list(network.keys())
    if ft:
        result = [s for s in result if ft in s.lower()]
    if dept != "ALL":
        result = [s for s in result
                  if departments.get(s, "").upper() == dept]
    render_cards(result)

# =========================================
# SHOW STUDENTS
# =========================================
def show_students(hi=None):
    show_cards_view()
    render_cards(hi_student=hi)

# =========================================
# ADD STUDENT
# =========================================
def open_add_student():
    win = make_popup("Add New Student", 440, 390)
    name_e = make_entry(win, "Full Name"); name_e.pack(pady=5)
    dept_e = make_entry(win, "Department  (CS / AI / SE …)"); dept_e.pack(pady=5)
    int_e  = make_entry(win, "Interests  (AI, DB, Web …)"); int_e.pack(pady=5)

    def save():
        name  = name_e.get().strip()
        dept  = dept_e.get().strip()
        inter = int_e.get().strip()
        if not (name and dept and inter):
            messagebox.showerror("Missing", "Fill all fields.", parent=win); return
        if name in network:
            messagebox.showerror("Duplicate", "Student already exists.", parent=win); return
        network[name] = []
        departments[name] = dept
        interests[name] = [i.strip() for i in inter.split(",")]
        save_data()
        log(f"Added → {name} | {dept}",
            toast=f"✔  {name} added", tc=SUCCESS)
        win.destroy(); show_students(hi=name)

    make_btn(win, "Save Student", save,
             color=SUCCESS, hover="#059669").pack(pady=18)

# =========================================
# EDIT STUDENT
# =========================================
def open_edit_student(student):
    win = make_popup("Edit Student", 460, 400)
    dept_e = make_entry(win, "Department")
    dept_e.insert(0, departments.get(student, ""))
    dept_e.pack(pady=6)
    int_e = make_entry(win, "Interests (comma separated)")
    int_e.insert(0, ", ".join(interests.get(student, [])))
    int_e.pack(pady=6)
    ctk.CTkLabel(win, text=f"Editing:  {student}",
                 font=("Arial", 11),
                 text_color=TEXT_MUTED).pack(pady=(4, 0))

    def save_edits():
        nd = dept_e.get().strip(); ni = int_e.get().strip()
        if not nd or not ni:
            messagebox.showerror("Missing", "Fill all fields.", parent=win); return
        departments[student] = nd
        interests[student] = [i.strip() for i in ni.split(",")]
        save_data()
        log(f"Updated → {student} | {nd}",
            toast=f"✔  {student} updated", tc=SUCCESS)
        win.destroy(); show_students(hi=student)

    make_btn(win, "Save Changes", save_edits,
             color=SUCCESS, hover="#059669").pack(pady=20)

# =========================================
# DELETE STUDENT
# =========================================
def do_delete_student(student):
    if not confirm_dialog(
        "Delete Student",
        f'Delete "{student}" and all their connections?\nThis cannot be undone.',
        "Delete", DANGER
    ): return
    for other in network:
        if student in network[other]:
            network[other].remove(student)
    del network[student]
    del departments[student]
    del interests[student]
    save_data()
    log(f"Deleted → {student}",
        toast=f"✖  {student} deleted", tc=DANGER)
    show_students()

# =========================================
# REMOVE CONNECTION
# =========================================
def open_remove_connection():
    win = make_popup("Remove Connection", 430, 320)
    s1 = make_entry(win, "First Student"); s1.pack(pady=7)
    s2 = make_entry(win, "Second Student"); s2.pack(pady=7)

    def remove():
        n1, n2 = s1.get().strip(), s2.get().strip()
        if n1 not in network or n2 not in network:
            messagebox.showerror("Not Found", "Student(s) not found.", parent=win); return
        if n2 not in network[n1]:
            messagebox.showerror("Not Connected",
                                 f"{n1} and {n2} are not connected.", parent=win); return
        if not confirm_dialog("Remove Connection",
                              f'Remove the connection between\n"{n1}" and "{n2}"?',
                              "Remove", WARNING): return
        network[n1].remove(n2); network[n2].remove(n1)
        save_data()
        log(f"Removed  {n1}  ↔  {n2}",
            toast=f"✖  {n1} ↔ {n2} disconnected", tc=WARNING)
        win.destroy(); show_students()

    make_btn(win, "Remove Connection", remove,
             color=WARNING, hover="#D97706").pack(pady=20)

# =========================================
# SEARCH STUDENT
# =========================================
def open_search_student():
    win = make_popup("Search Student", 420, 260)
    entry = make_entry(win, "Enter student name"); entry.pack(pady=10)

    def search():
        student = entry.get().strip(); win.destroy()
        if student not in network:
            show_log_view()
            set_out(sec("SEARCH") + "   Student not found.\n")
            show_toast("Student not found", DANGER); return
        show_students(hi=student)
        open_profile(student)
        show_toast(f"Found: {student}", SUCCESS)

    make_btn(win, "Search", search).pack(pady=14)

# =========================================
# CONNECT STUDENTS
# =========================================
def open_connect_students():
    win = make_popup("Connect Students", 420, 310)
    s1 = make_entry(win, "First Student"); s1.pack(pady=7)
    s2 = make_entry(win, "Second Student"); s2.pack(pady=7)

    def connect():
        n1, n2 = s1.get().strip(), s2.get().strip()
        if n1 not in network or n2 not in network:
            messagebox.showerror("Not Found", "Student(s) not found.", parent=win); return
        if n2 in network[n1]:
            messagebox.showerror("Exists", "Already connected.", parent=win); return
        network[n1].append(n2); network[n2].append(n1)
        save_data()
        log(f"Connected  {n1}  ↔  {n2}",
            toast=f"⟷  {n1} ↔ {n2}", tc=ACCENT)
        win.destroy(); show_students()

    make_btn(win, "Connect", connect,
             color=SUCCESS, hover="#059669").pack(pady=18)

# =========================================
# SHOW CONNECTIONS  — compact two-column cards
# =========================================
def show_connections():
    cw = ctk.CTkToplevel(app)
    cw.title("Social Connections")
    cw.geometry("700x560")
    cw.configure(fg_color=BG_DARK)
    cw.grab_set()

    ctk.CTkFrame(cw, height=4, fg_color=SUCCESS, corner_radius=0).pack(fill="x")
    hf = ctk.CTkFrame(cw, fg_color=BG_CARD, corner_radius=0)
    hf.pack(fill="x")
    ctk.CTkLabel(hf, text="  ◎  Social Connections",
                 font=("Arial", 16, "bold"),
                 text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=12)
    total_c = sum(len(v) for v in network.values()) // 2
    ctk.CTkLabel(hf, text=f"{total_c} total connections",
                 font=("Arial", 11), text_color=SUCCESS).pack(side="right", padx=20)

    scroll = ctk.CTkScrollableFrame(cw, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=16, pady=10)

    for student in network:
        dc   = dept_color(departments.get(student, "?"))
        dbc  = dept_bg_color(departments.get(student, "?"))
        inits = get_initials(student)
        conns = network[student]

        card = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10,
                            border_color=BORDER, border_width=1)
        card.pack(fill="x", pady=4)
        ctk.CTkFrame(card, width=4, fg_color=dc,
                     corner_radius=0).pack(side="left", fill="y")

        # student avatar
        av = ctk.CTkFrame(card, width=40, height=40, corner_radius=20,
                          fg_color=dbc, border_color=dc, border_width=2)
        av.pack(side="left", padx=(10, 8), pady=9)
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=inits, font=("Arial", 12, "bold"),
                     text_color=dc).place(relx=0.5, rely=0.5, anchor="center")

        # name
        ctk.CTkLabel(card, text=student, font=("Arial", 13, "bold"),
                     text_color=TEXT_PRIMARY, width=120,
                     anchor="w").pack(side="left", pady=9)

        # arrow
        ctk.CTkLabel(card, text="⟷", font=("Arial", 14),
                     text_color=TEXT_MUTED).pack(side="left", padx=6)

        # connection chips
        chips_f = ctk.CTkFrame(card, fg_color="transparent")
        chips_f.pack(side="left", fill="x", expand=True, pady=7)

        if conns:
            for cf in conns:
                cf_dc  = dept_color(departments.get(cf, "?"))
                cf_dbc = dept_bg_color(departments.get(cf, "?"))
                chip = ctk.CTkFrame(chips_f, fg_color=cf_dbc,
                                    corner_radius=16,
                                    border_color=cf_dc, border_width=1)
                chip.pack(side="left", padx=3, pady=2)
                ctk.CTkLabel(chip, text=f"  {cf}  ",
                             font=("Arial", 10, "bold"),
                             text_color=cf_dc).pack(pady=3)
        else:
            ctk.CTkLabel(chips_f, text="No connections",
                         font=("Arial", 10), text_color=TEXT_MUTED).pack(
                side="left", padx=6)

        # count badge
        cb = ctk.CTkFrame(card, fg_color="#0A2018", corner_radius=7)
        cb.pack(side="right", padx=10, pady=9)
        ctk.CTkLabel(cb, text=f" {len(conns)} ",
                     font=("Arial", 13, "bold"),
                     text_color=SUCCESS).pack(padx=2)

    ctk.CTkButton(cw, text="Close", height=34, corner_radius=8,
                  fg_color=BG_INNER, hover_color=BORDER,
                  text_color=TEXT_MUTED, font=("Arial", 12, "bold"),
                  command=cw.destroy).pack(fill="x", padx=16, pady=8)

# =========================================
# INTEREST MATCHING
# =========================================
def open_interest_matching():
    win = make_popup("Interest Matching", 420, 260)
    entry = make_entry(win, "Enter interest  (e.g. AI, DB, Web)"); entry.pack(pady=10)

    def find():
        kw = entry.get().strip().lower(); win.destroy()
        matched = [s for s in interests
                   if kw in [t.lower() for t in interests[s]]]
        show_cards_view()
        render_cards(matched, hi_interest=kw)
        show_toast(f"Found {len(matched)} match(es) for '{kw}'",
                   SUCCESS if matched else DANGER)

    make_btn(win, "Find Students", find).pack(pady=14)

# =========================================
# SHORTEST PATH  (BFS)
# =========================================
def open_shortest_path():
    win = make_popup("Shortest Path (BFS)", 440, 320)
    start_e = make_entry(win, "Start Student"); start_e.pack(pady=7)
    end_e   = make_entry(win, "Target Student"); end_e.pack(pady=7)

    def find_path():
        start = start_e.get().strip(); end = end_e.get().strip()
        if start not in network or end not in network:
            messagebox.showerror("Not Found", "Student not found.", parent=win); return
        queue = deque([start]); visited = {start: True}; parent = {}
        while queue:
            curr = queue.popleft()
            if curr == end: break
            for nb in network[curr]:
                if nb not in visited:
                    visited[nb] = True; parent[nb] = curr; queue.append(nb)
        win.destroy()

        if end not in visited:
            show_toast("No connection path found", DANGER); return

        path, tmp = [], end
        while tmp != start:
            path.append(tmp); tmp = parent[tmp]
        path.append(start); path.reverse()

        # ── visual popup
        pw = ctk.CTkToplevel(app)
        pw.title("Shortest Connection Path")
        pw.geometry("680x420")
        pw.configure(fg_color=BG_DARK)
        pw.grab_set()
        pw.resizable(False, False)

        ctk.CTkFrame(pw, height=4, fg_color=ACCENT, corner_radius=0).pack(fill="x")
        hf = ctk.CTkFrame(pw, fg_color=BG_CARD, corner_radius=0)
        hf.pack(fill="x")
        ctk.CTkLabel(hf, text="  ↝  Shortest Connection Path",
                     font=("Arial", 16, "bold"),
                     text_color=ACCENT).pack(side="left", padx=20, pady=12)
        bp = ctk.CTkFrame(hf, fg_color=BG_INNER, corner_radius=20)
        bp.pack(side="right", padx=16, pady=10)
        ctk.CTkLabel(bp, text=f"  {len(path)-1} hop(s)  •  {len(path)} students  ",
                     font=("Arial", 11, "bold"),
                     text_color=ACCENT).pack(pady=4)

        body = ctk.CTkScrollableFrame(pw, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=12)

        # ── visual node chain (scrollable horizontal row)
        chain_outer = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=12,
                                   border_color=BORDER, border_width=1)
        chain_outer.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(chain_outer, text="PATH VISUALIZATION",
                     font=("Arial", 9, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))

        chain_row = ctk.CTkFrame(chain_outer, fg_color="transparent")
        chain_row.pack(anchor="center", pady=(0, 12))

        for i, name in enumerate(path):
            d_    = departments.get(name, "?")
            dc_   = dept_color(d_)
            dbc_  = dept_bg_color(d_)
            ini_  = get_initials(name)

            nf = ctk.CTkFrame(chain_row, fg_color="transparent")
            nf.pack(side="left", padx=4)

            av = ctk.CTkFrame(nf, width=52, height=52, corner_radius=26,
                              fg_color=dbc_, border_color=dc_, border_width=2)
            av.pack()
            av.pack_propagate(False)
            ctk.CTkLabel(av, text=ini_, font=("Arial", 14, "bold"),
                         text_color=dc_
                         ).place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(nf, text=name, font=("Arial", 9, "bold"),
                         text_color=TEXT_PRIMARY, wraplength=64,
                         justify="center").pack(pady=(4, 0))
            dp_ = ctk.CTkFrame(nf, fg_color=dbc_, corner_radius=4)
            dp_.pack(pady=2)
            ctk.CTkLabel(dp_, text=f" {d_} ", font=("Arial", 8, "bold"),
                         text_color=dc_).pack()

            if i < len(path) - 1:
                ctk.CTkLabel(chain_row, text="→",
                             font=("Arial", 18, "bold"),
                             text_color=ACCENT).pack(side="left", padx=2)

        # ── step-by-step cards
        ctk.CTkLabel(body, text="STEP BY STEP",
                     font=("Arial", 10, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        for i in range(len(path) - 1):
            a, b = path[i], path[i+1]
            sc = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=8,
                              border_color=BORDER, border_width=1)
            sc.pack(fill="x", pady=3)
            ctk.CTkFrame(sc, width=4, fg_color=ACCENT,
                         corner_radius=0).pack(side="left", fill="y")

            num = ctk.CTkFrame(sc, fg_color=BG_INNER, corner_radius=6,
                               width=26, height=26)
            num.pack(side="left", padx=(10, 0), pady=9)
            num.pack_propagate(False)
            ctk.CTkLabel(num, text=str(i+1), font=("Arial", 10, "bold"),
                         text_color=ACCENT).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(sc, text=f"  {a}  →  {b}",
                         font=("Arial", 12), text_color=TEXT_PRIMARY,
                         anchor="w").pack(side="left", padx=8, pady=9)

        ctk.CTkButton(pw, text="Close", height=34, corner_radius=8,
                      fg_color=BG_INNER, hover_color=BORDER,
                      text_color=TEXT_MUTED, font=("Arial", 12, "bold"),
                      command=pw.destroy).pack(fill="x", padx=16, pady=8)

        show_toast(f"Path: {len(path)-1} hop(s)", SUCCESS)

    make_btn(win, "Find Path", find_path).pack(pady=18)

# =========================================
# MUTUAL FRIENDS
# =========================================
def open_mutual_friends():
    win = make_popup("Friend Suggestions", 420, 260)
    entry = make_entry(win, "Enter student name"); entry.pack(pady=10)

    def find():
        student = entry.get().strip()
        if student not in network:
            messagebox.showerror("Not Found", "Student not found.", parent=win); return
        suggestions = {}
        for friend in network[student]:
            for mutual in network[friend]:
                if mutual != student and mutual not in network[student]:
                    suggestions.setdefault(mutual, []).append(friend)
        win.destroy()
        if not suggestions:
            show_log_view()
            set_out(sec(f"FRIEND SUGGESTIONS — {student.upper()}") +
                    "   No suggestions found.\n")
            show_toast("No suggestions found", DANGER); return

        sw = ctk.CTkToplevel(app)
        sw.title(f"Suggestions for {student}")
        sw.geometry("720x580")
        sw.configure(fg_color=BG_DARK)
        sw.grab_set()

        ctk.CTkFrame(sw, height=4, fg_color=SUCCESS,
                     corner_radius=0).pack(fill="x")
        hf = ctk.CTkFrame(sw, fg_color=BG_CARD, corner_radius=0)
        hf.pack(fill="x")
        ctk.CTkLabel(hf, text=f"  Friend Suggestions  —  {student}",
                     font=("Arial", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=14)
        ctk.CTkLabel(hf, text=f"{len(suggestions)} suggestion(s)",
                     font=("Arial", 12),
                     text_color=SUCCESS).pack(side="right", padx=20)

        scroll = ctk.CTkScrollableFrame(sw, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=12)
        student_interests = set(interests.get(student, []))

        for person, via_list in suggestions.items():
            p_dept  = departments.get(person, "?")
            p_dc    = dept_color(p_dept)
            p_dbc   = dept_bg_color(p_dept)
            p_inits = get_initials(person)
            p_tags  = interests.get(person, [])
            p_conns = network.get(person, [])
            shared  = student_interests & set(p_tags)

            card = ctk.CTkFrame(scroll, fg_color=BG_CARD,
                                corner_radius=12,
                                border_color=p_dc, border_width=1)
            card.pack(fill="x", pady=6)
            ctk.CTkFrame(card, width=5, fg_color=p_dc,
                         corner_radius=0).pack(side="left", fill="y")

            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(side="left", fill="both", expand=True, padx=14, pady=12)

            top = ctk.CTkFrame(body, fg_color="transparent")
            top.pack(fill="x")
            av = ctk.CTkFrame(top, width=52, height=52, corner_radius=26,
                              fg_color=p_dbc, border_color=p_dc, border_width=2)
            av.pack(side="left")
            av.pack_propagate(False)
            ctk.CTkLabel(av, text=p_inits, font=("Arial", 16, "bold"),
                         text_color=p_dc
                         ).place(relx=0.5, rely=0.5, anchor="center")
            nc = ctk.CTkFrame(top, fg_color="transparent")
            nc.pack(side="left", padx=12, anchor="w")
            ctk.CTkLabel(nc, text=person, font=("Arial", 14, "bold"),
                         text_color=TEXT_PRIMARY).pack(anchor="w")
            dp = ctk.CTkFrame(nc, fg_color=p_dbc, corner_radius=5)
            dp.pack(anchor="w", pady=2)
            ctk.CTkLabel(dp, text=f"  {p_dept}  ",
                         font=("Arial", 10, "bold"),
                         text_color=p_dc).pack()
            sc_col = ctk.CTkFrame(top, fg_color="transparent")
            sc_col.pack(side="right", anchor="e")
            for icon, val, color in [("⟷", len(p_conns), SUCCESS),
                                      ("◈", len(via_list), ACCENT)]:
                pf = ctk.CTkFrame(sc_col, fg_color=BG_INNER, corner_radius=7)
                pf.pack(side="left", padx=3)
                ctk.CTkLabel(pf, text=f"  {icon} {val}  ",
                             font=("Arial", 11, "bold"),
                             text_color=color).pack(pady=4)

            mr = ctk.CTkFrame(body, fg_color="transparent")
            mr.pack(fill="x", pady=(8, 0))
            ctk.CTkLabel(mr, text="Mutual connections:",
                         font=("Arial", 10),
                         text_color=TEXT_MUTED).pack(side="left")
            for vf in via_list:
                vf_dc  = dept_color(departments.get(vf, "?"))
                vf_dbc = dept_bg_color(departments.get(vf, "?"))
                vf_ini = get_initials(vf)
                chip = ctk.CTkFrame(mr, fg_color=BG_INNER, corner_radius=20)
                chip.pack(side="left", padx=4, pady=2)
                ic2 = ctk.CTkFrame(chip, fg_color="transparent")
                ic2.pack(padx=6, pady=3)
                mav = ctk.CTkFrame(ic2, width=20, height=20, corner_radius=10,
                                   fg_color=vf_dbc, border_color=vf_dc, border_width=1)
                mav.pack(side="left")
                mav.pack_propagate(False)
                ctk.CTkLabel(mav, text=vf_ini[0], font=("Arial", 8, "bold"),
                             text_color=vf_dc
                             ).place(relx=0.5, rely=0.5, anchor="center")
                ctk.CTkLabel(ic2, text=f"  {vf}",
                             font=("Arial", 10, "bold"),
                             text_color=TEXT_PRIMARY).pack(side="left")

            if shared:
                ir = ctk.CTkFrame(body, fg_color="transparent")
                ir.pack(fill="x", pady=(6, 0))
                ctk.CTkLabel(ir, text="Shared interests:",
                             font=("Arial", 10),
                             text_color=TEXT_MUTED).pack(side="left")
                for tag in shared:
                    tp = ctk.CTkFrame(ir, fg_color=BG_TAG, corner_radius=5)
                    tp.pack(side="left", padx=3, pady=2)
                    ctk.CTkLabel(tp, text=f" {tag} ",
                                 font=("Arial", 10),
                                 text_color=WARNING).pack()

            def on_connect(p=person, s=student):
                if p not in network[s]:
                    network[s].append(p); network[p].append(s)
                    save_data()
                    show_toast(f"Connected  {s}  ↔  {p}", SUCCESS)
                    show_students(); sw.destroy()

            ctk.CTkButton(card, text="+ Connect",
                          width=90, height=32, corner_radius=7,
                          fg_color=SUCCESS, hover_color="#059669",
                          text_color="white", font=("Arial", 11, "bold"),
                          command=on_connect
                          ).pack(side="right", padx=14, pady=12)

        show_toast(f"Found {len(suggestions)} suggestion(s)", SUCCESS)

    make_btn(win, "Find Suggestions", find).pack(pady=14)

# =========================================
# MOST POPULAR
# =========================================
def show_popular():
    if not network:
        show_log_view()
        set_out(sec("MOST POPULAR") + "   No students yet.\n"); return
    popular = max(network, key=lambda s: len(network[s]))
    show_students(hi=popular)
    open_profile(popular)
    show_toast(f"★  {popular}  —  {len(network[popular])} connections", WARNING)

# =========================================
# SMART STUDY PARTNER  — balanced 2-col reason grid
# =========================================
def open_study_partner():
    win = make_popup("Smart Study Partner", 440, 260)
    entry = make_entry(win, "Enter student name"); entry.pack(pady=10)

    def recommend():
        student = entry.get().strip()
        if student not in network:
            messagebox.showerror("Not Found", "Student not found.", parent=win); return
        best, top_score, reason = None, -1, []
        for other in network:
            if other == student: continue
            sc, cr = 0, []
            if departments.get(student) == departments.get(other):
                sc += 3; cr.append(("Same Department", SUCCESS))
            common = set(interests.get(student, [])) & set(interests.get(other, []))
            if common:
                sc += len(common) * 2
                cr.append(("Shared Interests: " + ", ".join(common), WARNING))
            mutual = set(network.get(student, [])) & set(network.get(other, []))
            if mutual:
                sc += len(mutual)
                cr.append(("Mutual Connections: " + ", ".join(mutual), ACCENT))
            if sc > top_score:
                top_score, best, reason = sc, other, cr
        win.destroy()
        if not best:
            show_log_view()
            set_out(sec("SMART STUDY PARTNER") + "   No suitable partner found.\n")
            show_toast("No partner found", DANGER); return

        # ── auto-size based on reason count
        reason_h = len(reason) * 56
        win_h    = min(max(460, 310 + reason_h), 620)

        rw = ctk.CTkToplevel(app)
        rw.title("Smart Study Partner")
        rw.geometry(f"560x{win_h}")
        rw.configure(fg_color=BG_DARK)
        rw.grab_set()
        rw.resizable(False, False)

        b_dept  = departments.get(best, "?")
        b_dc    = dept_color(b_dept)
        b_dbc   = dept_bg_color(b_dept)
        b_inits = get_initials(best)
        b_tags  = interests.get(best, [])
        b_conns = network.get(best, [])
        shared  = set(interests.get(student, [])) & set(b_tags)

        # top bar + header
        ctk.CTkFrame(rw, height=5, fg_color=WARNING,
                     corner_radius=0).pack(fill="x")
        hf = ctk.CTkFrame(rw, fg_color=BG_CARD, corner_radius=0)
        hf.pack(fill="x")
        ctk.CTkLabel(hf, text="  ⚙  Smart Study Partner",
                     font=("Arial", 16, "bold"),
                     text_color=WARNING).pack(side="left", padx=20, pady=12)
        sp = ctk.CTkFrame(hf, fg_color="#2D1F00", corner_radius=20)
        sp.pack(side="right", padx=20, pady=10)
        ctk.CTkLabel(sp, text=f"  Match Score: {top_score} pts  ",
                     font=("Arial", 12, "bold"),
                     text_color=WARNING).pack(pady=4)

        # scrollable body
        body = ctk.CTkScrollableFrame(rw, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=10)

        # ── partner card (compact, side-by-side layout)
        card = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=14,
                            border_color=b_dc, border_width=2)
        card.pack(fill="x", pady=(0, 14))
        ctk.CTkFrame(card, height=5, fg_color=b_dc,
                     corner_radius=0).pack(fill="x")

        ct = ctk.CTkFrame(card, fg_color="transparent")
        ct.pack(fill="x", padx=16, pady=(12, 10))

        av = ctk.CTkFrame(ct, width=60, height=60, corner_radius=30,
                          fg_color=b_dbc, border_color=b_dc, border_width=3)
        av.pack(side="left")
        av.pack_propagate(False)
        ctk.CTkLabel(av, text=b_inits, font=("Arial", 20, "bold"),
                     text_color=b_dc).place(relx=0.5, rely=0.5, anchor="center")

        ic = ctk.CTkFrame(ct, fg_color="transparent")
        ic.pack(side="left", padx=14, anchor="w")
        ctk.CTkLabel(ic, text=best, font=("Arial", 17, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        dp2 = ctk.CTkFrame(ic, fg_color=b_dbc, corner_radius=6)
        dp2.pack(anchor="w", pady=3)
        ctk.CTkLabel(dp2, text=f"  {b_dept} Department  ",
                     font=("Arial", 11, "bold"),
                     text_color=b_dc).pack()

        st = ctk.CTkFrame(ct, fg_color="transparent")
        st.pack(side="right", anchor="e")
        for icon, val, col in [("⟷", len(b_conns), SUCCESS),
                                ("◈", len(b_tags), ACCENT)]:
            pf = ctk.CTkFrame(st, fg_color=BG_INNER, corner_radius=7)
            pf.pack(side="left", padx=3)
            ctk.CTkLabel(pf, text=f"  {icon} {val}  ",
                         font=("Arial", 12, "bold"),
                         text_color=col).pack(pady=5)

        if b_tags:
            ctk.CTkFrame(card, height=1, fg_color=BORDER,
                         corner_radius=0).pack(fill="x", padx=14, pady=(0, 2))
            tr = ctk.CTkFrame(card, fg_color="transparent")
            tr.pack(fill="x", padx=14, pady=(4, 10))
            for tag in b_tags[:6]:
                tp = ctk.CTkFrame(tr, fg_color=BG_TAG, corner_radius=5)
                tp.pack(side="left", padx=3, pady=2)
                ctk.CTkLabel(tp, text=f" {tag} ", font=("Arial", 11),
                             text_color=WARNING if tag in shared
                             else ACCENT).pack()

        # ── WHY THIS MATCH — balanced 2-column grid
        rh = ctk.CTkFrame(body, fg_color="transparent")
        rh.pack(fill="x", pady=(4, 8))
        ctk.CTkLabel(rh, text="WHY THIS MATCH?",
                     font=("Arial", 11, "bold"),
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(rh, text=f"{len(reason)} reason(s)",
                     font=("Arial", 10),
                     text_color=TEXT_MUTED).pack(side="right")

        # 2-column grid for reasons so they sit side by side (balanced)
        rg = ctk.CTkFrame(body, fg_color="transparent")
        rg.pack(fill="x", pady=(0, 4))
        rg.grid_columnconfigure(0, weight=1)
        rg.grid_columnconfigure(1, weight=1)

        for i, (txt, color) in enumerate(reason):
            rc = ctk.CTkFrame(rg, fg_color=BG_CARD, corner_radius=9,
                              border_color=BORDER, border_width=1)
            # if odd number and last item → span both columns
            if len(reason) % 2 == 1 and i == len(reason) - 1:
                rc.grid(row=i // 2, column=0, columnspan=2,
                        padx=4, pady=4, sticky="ew")
            else:
                rc.grid(row=i // 2, column=i % 2,
                        padx=4, pady=4, sticky="ew")

            # colored left strip
            ctk.CTkFrame(rc, width=4, fg_color=color,
                         corner_radius=0).pack(side="left", fill="y")
            # icon circle
            icf = ctk.CTkFrame(rc, width=28, height=28, corner_radius=14,
                               fg_color=BG_INNER, border_color=color, border_width=1)
            icf.pack(side="left", padx=(8, 0), pady=8)
            icf.pack_propagate(False)
            ctk.CTkLabel(icf, text="✔", font=("Arial", 11, "bold"),
                         text_color=color
                         ).place(relx=0.5, rely=0.5, anchor="center")
            # reason text (wraplength fits half-width)
            ctk.CTkLabel(rc, text=txt, font=("Arial", 11),
                         text_color=TEXT_PRIMARY, anchor="w",
                         wraplength=200).pack(side="left", padx=8, pady=10)

        # close button
        ctk.CTkButton(rw, text="Close",
                      height=36, corner_radius=8,
                      fg_color=BG_INNER, hover_color=BORDER,
                      text_color=TEXT_MUTED, font=("Arial", 13, "bold"),
                      command=rw.destroy
                      ).pack(fill="x", padx=18, pady=(4, 10))

        show_toast(f"Best match: {best}  ({top_score} pts)", SUCCESS)

    make_btn(win, "Find Partner", recommend,
             color=WARNING, hover="#D97706").pack(pady=14)

# =========================================
# VISUALIZE (NetworkX)
# =========================================
def visualize_network():
    if not network:
        messagebox.showerror("Empty", "No students in network."); return
    G = nx.Graph()
    for s in network:
        G.add_node(s)
        for f in network[s]: G.add_edge(s, f)
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.patch.set_facecolor("#0A0E1A")
    ax.set_facecolor("#0D1117")
    pos = nx.spring_layout(G, seed=42, k=1.8)
    degrees = dict(G.degree())
    node_sizes  = [700 + degrees[n]*300 for n in G.nodes()]
    node_colors = [dept_color(departments.get(n, "CS")) for n in G.nodes()]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#2A3A4A", width=1.5)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                           node_color=node_colors, alpha=0.95)
    nx.draw_networkx_labels(G, pos, ax=ax, font_color="white",
                            font_size=9, font_weight="bold")
    ax.set_title("Campus Social Network", color=ACCENT,
                 fontsize=16, fontweight="bold", pad=18)
    ax.axis("off")
    plt.tight_layout(); plt.show()

# =========================================
# LIVE DASHBOARD
# =========================================
def show_dashboard():
    if not network:
        messagebox.showerror("Empty", "No students added yet."); return

    n       = len(network)
    c       = sum(len(v) for v in network.values()) // 2
    avg_c   = round(c / n, 2) if n else 0
    density = round((2 * c) / (n * (n - 1)), 3) if n > 1 else 0.0
    ranked  = sorted(network.keys(), key=lambda s: len(network[s]), reverse=True)
    top3    = ranked[:3]
    dept_cnt = {}
    for d in departments.values():
        dept_cnt[d] = dept_cnt.get(d, 0) + 1
    active_dept = max(dept_cnt, key=dept_cnt.get) if dept_cnt else "—"
    int_cnt = {}
    for tags in interests.values():
        for t in tags: int_cnt[t.strip()] = int_cnt.get(t.strip(), 0) + 1
    top_interest = max(int_cnt, key=int_cnt.get) if int_cnt else "—"
    score = 0
    if n >= 5: score += 25
    elif n >= 2: score += 10
    if density >= 0.5: score += 30
    elif density >= 0.2: score += 15
    if avg_c >= 3: score += 25
    elif avg_c >= 1: score += 12
    if c >= 5: score += 20
    elif c >= 1: score += 10
    score = min(score, 100)
    if score >= 80: hl, hc = "Excellent", SUCCESS
    elif score >= 55: hl, hc = "Good", ACCENT
    elif score >= 30: hl, hc = "Fair", WARNING
    else: hl, hc = "Sparse", DANGER

    dw = ctk.CTkToplevel(app)
    dw.title("Live Analytics Dashboard")
    dw.geometry("780x660")
    dw.configure(fg_color=BG_DARK)
    dw.grab_set()
    dw.resizable(False, False)

    tb = ctk.CTkFrame(dw, height=5, fg_color="transparent", corner_radius=0)
    tb.pack(fill="x"); tb.pack_propagate(False)
    for col in [ACCENT2, ACCENT, SUCCESS]:
        ctk.CTkFrame(tb, height=5, fg_color=col,
                     corner_radius=0).pack(side="left", expand=True, fill="y")

    hdr = ctk.CTkFrame(dw, fg_color=BG_CARD, corner_radius=0)
    hdr.pack(fill="x")
    ctk.CTkLabel(hdr, text="  ◫  Live Analytics Dashboard",
                 font=("Arial", 18, "bold"),
                 text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=14)
    hp = ctk.CTkFrame(hdr, fg_color=BG_INNER, corner_radius=20)
    hp.pack(side="right", padx=16, pady=12)
    ctk.CTkLabel(hp, text=f"  Network Health: ",
                 font=("Arial", 11),
                 text_color=TEXT_MUTED).pack(side="left", padx=(10, 0), pady=6)
    ctk.CTkLabel(hp, text=f"{hl}  ({score}/100)  ",
                 font=("Arial", 12, "bold"),
                 text_color=hc).pack(side="left", pady=6)

    body = ctk.CTkScrollableFrame(dw, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=18, pady=12)

    def stat_card(parent, icon, label, value, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12,
                         border_color=BORDER, border_width=1)
        f.pack(side="left", expand=True, fill="x", padx=4)
        ctk.CTkLabel(f, text=icon, font=("Arial", 20),
                     text_color=color).pack(pady=(12, 2))
        ctk.CTkLabel(f, text=str(value), font=("Arial", 22, "bold"),
                     text_color=color).pack()
        ctk.CTkLabel(f, text=label, font=("Arial", 9),
                     text_color=TEXT_MUTED).pack(pady=(0, 12))

    sr = ctk.CTkFrame(body, fg_color="transparent")
    sr.pack(fill="x", pady=(0, 14))
    stat_card(sr, "◈", "STUDENTS",       n,             ACCENT)
    stat_card(sr, "⟷", "CONNECTIONS",    c,             SUCCESS)
    stat_card(sr, "⬡", "DEPARTMENTS",    len(dept_cnt), WARNING)
    stat_card(sr, "≈", "AVG CONN.",      avg_c,         ACCENT2)
    stat_card(sr, "◉", "DENSITY",        density,       "#EC4899")
    stat_card(sr, "★", "TOP INTEREST",   top_interest,  WARNING)

    row2 = ctk.CTkFrame(body, fg_color="transparent")
    row2.pack(fill="x", pady=(0, 14))

    # bar chart
    chart_card = ctk.CTkFrame(row2, fg_color=BG_CARD, corner_radius=12,
                               border_color=BORDER, border_width=1)
    chart_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
    ctk.CTkLabel(chart_card, text="  Department Breakdown",
                 font=("Arial", 12, "bold"),
                 text_color=TEXT_PRIMARY, anchor="w"
                 ).pack(fill="x", padx=14, pady=(12, 6))
    ctk.CTkFrame(chart_card, height=1, fg_color=BORDER,
                 corner_radius=0).pack(fill="x", padx=14, pady=(0, 8))

    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    fig2 = Figure(figsize=(4.0, 2.2), dpi=90)
    fig2.patch.set_facecolor("#111827")
    ax2 = fig2.add_subplot(111)
    ax2.set_facecolor("#111827")
    if dept_cnt:
        sd = sorted(dept_cnt.items())
        labels2 = [d for d, _ in sd]; vals2 = [v for _, v in sd]
        colors2 = [dept_color(d) for d in labels2]
        bars2 = ax2.bar(labels2, vals2, color=colors2, width=0.55, zorder=3)
        for bar2, val2 in zip(bars2, vals2):
            ax2.text(bar2.get_x() + bar2.get_width() / 2,
                     bar2.get_height() + 0.06, str(val2),
                     ha="center", va="bottom", color="white",
                     fontsize=8, fontweight="bold")
        ax2.set_yticks(range(0, max(vals2) + 2))
        ax2.yaxis.set_tick_params(labelcolor="#4A6080", labelsize=7)
        ax2.xaxis.set_tick_params(labelcolor="#8BA5C0", labelsize=8)
        for sp in ["top", "right"]: ax2.spines[sp].set_visible(False)
        ax2.spines["left"].set_color("#1F2937")
        ax2.spines["bottom"].set_color("#1F2937")
        ax2.yaxis.grid(True, color="#1F2937", linewidth=0.6, zorder=0)
        ax2.set_axisbelow(True)
    fig2.tight_layout(pad=0.6)
    cv = FigureCanvasTkAgg(fig2, master=chart_card)
    cv.draw(); cv.get_tk_widget().pack(padx=10, pady=(0, 12))

    # leaderboard
    lb_card = ctk.CTkFrame(row2, fg_color=BG_CARD, corner_radius=12,
                            border_color=BORDER, border_width=1, width=290)
    lb_card.pack(side="left", fill="y", padx=(6, 0))
    lb_card.pack_propagate(False)
    ctk.CTkLabel(lb_card, text="  ★  Top Connected",
                 font=("Arial", 12, "bold"),
                 text_color=TEXT_PRIMARY, anchor="w"
                 ).pack(fill="x", padx=14, pady=(12, 6))
    ctk.CTkFrame(lb_card, height=1, fg_color=BORDER,
                 corner_radius=0).pack(fill="x", padx=14, pady=(0, 8))
    medals = ["🥇", "🥈", "🥉"]
    medal_colors = [WARNING, TEXT_MUTED, "#CD7F32"]
    for rank, name2 in enumerate(top3):
        dc2  = dept_color(departments.get(name2, "?"))
        dbc2 = dept_bg_color(departments.get(name2, "?"))
        ini2 = get_initials(name2)
        cn   = len(network.get(name2, []))
        dep2 = departments.get(name2, "?")
        rr = ctk.CTkFrame(lb_card, fg_color=BG_INNER, corner_radius=10)
        rr.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(rr, text=medals[rank], font=("Arial", 18),
                     text_color=medal_colors[rank]
                     ).pack(side="left", padx=(10, 6), pady=10)
        mav = ctk.CTkFrame(rr, width=36, height=36, corner_radius=18,
                           fg_color=dbc2, border_color=dc2, border_width=2)
        mav.pack(side="left", pady=8)
        mav.pack_propagate(False)
        ctk.CTkLabel(mav, text=ini2, font=("Arial", 12, "bold"),
                     text_color=dc2
                     ).place(relx=0.5, rely=0.5, anchor="center")
        inf2 = ctk.CTkFrame(rr, fg_color="transparent")
        inf2.pack(side="left", padx=8, anchor="w", pady=8)
        ctk.CTkLabel(inf2, text=name2, font=("Arial", 12, "bold"),
                     text_color=TEXT_PRIMARY, wraplength=90).pack(anchor="w")
        dp3 = ctk.CTkFrame(inf2, fg_color=dbc2, corner_radius=4)
        dp3.pack(anchor="w", pady=1)
        ctk.CTkLabel(dp3, text=f"  {dep2}  ", font=("Arial", 9, "bold"),
                     text_color=dc2).pack()
        cb = ctk.CTkFrame(rr, fg_color="#0A2018", corner_radius=8)
        cb.pack(side="right", padx=10, pady=8)
        ctk.CTkLabel(cb, text=f"  {cn}  ", font=("Arial", 14, "bold"),
                     text_color=SUCCESS).pack()
        ctk.CTkLabel(cb, text="conn", font=("Arial", 8),
                     text_color=TEXT_MUTED).pack(pady=(0, 4))

    row3 = ctk.CTkFrame(body, fg_color="transparent")
    row3.pack(fill="x", pady=(0, 8))
    def extra_pill(parent, label, value, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10,
                         border_color=BORDER, border_width=1)
        f.pack(side="left", expand=True, fill="x", padx=4)
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(pady=10, padx=14)
        ctk.CTkLabel(inner, text=label, font=("Arial", 9),
                     text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(inner, text=f"  {value}",
                     font=("Arial", 12, "bold"),
                     text_color=color).pack(side="left")
    extra_pill(row3, "Most Popular", top3[0] if top3 else "—", WARNING)
    extra_pill(row3, "Active Dept.", active_dept, ACCENT)
    extra_pill(row3, "Top Interest", top_interest, SUCCESS)
    extra_pill(row3, "Density",      f"{density:.3f}", ACCENT2)

    ctk.CTkButton(dw, text="Close",
                  height=38, corner_radius=8,
                  fg_color=BG_INNER, hover_color=BORDER,
                  text_color=TEXT_MUTED, font=("Arial", 13, "bold"),
                  command=dw.destroy
                  ).pack(fill="x", padx=18, pady=12)
    show_toast("Dashboard opened", ACCENT2)

# =====================================================================
#  BUILD UI
# =====================================================================
app = ctk.CTk()
app.title("Intelligent Campus Networking System")
app.geometry("1560x900")
app.minsize(1100, 700)
app.configure(fg_color=BG_DARK)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
sidebar = ctk.CTkFrame(app, width=230, corner_radius=0,
                       fg_color=BG_SIDEBAR,
                       border_color=BORDER, border_width=1)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

ctk.CTkFrame(sidebar, height=4, fg_color=ACCENT,
             corner_radius=0).pack(fill="x")

# ── STYLISH TEXT LOGO (no canvas)
logo_f = ctk.CTkFrame(sidebar, fg_color="transparent")
logo_f.pack(pady=(18, 4))

brand_row = ctk.CTkFrame(logo_f, fg_color="transparent")
brand_row.pack()
ctk.CTkLabel(brand_row, text="CAMPUS",
             font=("Arial", 18, "bold"),
             text_color=ACCENT).pack(side="left")
ctk.CTkLabel(brand_row, text="NET",
             font=("Arial", 18, "bold"),
             text_color=TEXT_PRIMARY).pack(side="left")

ctk.CTkLabel(logo_f,
             text="◦  Intelligent Networking  ◦",
             font=("Arial", 9),
             text_color=TEXT_MUTED).pack(pady=(2, 0))

ctk.CTkFrame(sidebar, height=1, fg_color=BORDER,
             corner_radius=0).pack(fill="x", padx=16, pady=(10, 2))

nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
nav_scroll.pack(fill="both", expand=True)

def nav_sec(text):
    ctk.CTkLabel(nav_scroll, text=text, font=("Arial", 9, "bold"),
                 text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(12, 2))

def nav_btn(icon, text, cmd, ac=ACCENT):
    btn = ctk.CTkButton(nav_scroll, text=f" {icon}  {text}",
                        command=cmd, anchor="w",
                        height=34, corner_radius=7,
                        fg_color="transparent", hover_color=BG_INNER,
                        text_color=TEXT_PRIMARY, font=("Arial", 12, "bold"),
                        border_spacing=4)
    btn.pack(fill="x", padx=8, pady=1)
    btn.bind("<Enter>", lambda e: btn.configure(text_color=ac))
    btn.bind("<Leave>", lambda e: btn.configure(text_color=TEXT_PRIMARY))

nav_sec("STUDENTS")
nav_btn("＋", "Add Student",       open_add_student,      ACCENT)
nav_btn("⌕", "Search Student",     open_search_student,   ACCENT)
nav_btn("≡", "Show All Students",  show_students,          ACCENT)

nav_sec("CONNECTIONS")
nav_btn("⟷", "Connect Students",  open_connect_students,  SUCCESS)
nav_btn("✕", "Remove Connection",  open_remove_connection, DANGER)
nav_btn("◎", "Show Connections",   show_connections,        SUCCESS)
nav_btn("◈", "Mutual Friends",     open_mutual_friends,     SUCCESS)
nav_btn("↝", "Shortest Path",      open_shortest_path,      SUCCESS)

nav_sec("DISCOVERY")
nav_btn("◉", "Interest Matching",  open_interest_matching, WARNING)
nav_btn("★", "Most Popular",        show_popular,           WARNING)
nav_btn("⚙", "Study Partner",       open_study_partner,     WARNING)

nav_sec("ANALYTICS")
nav_btn("◫", "Live Dashboard",     show_dashboard,    ACCENT2)
nav_btn("⬡", "Visualize Network",  visualize_network, ACCENT2)

ctk.CTkFrame(sidebar, height=1, fg_color=BORDER,
             corner_radius=0).pack(fill="x", padx=16, pady=(6, 0))
ctk.CTkLabel(sidebar, text="v8.0  •  Python / CustomTkinter",
             font=("Arial", 9),
             text_color=TEXT_MUTED).pack(pady=8)

# ─────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────
main_frame = ctk.CTkFrame(app, fg_color=BG_DARK, corner_radius=0)
main_frame.pack(side="right", fill="both", expand=True)

# ── TOP BAR
topbar = ctk.CTkFrame(main_frame, height=56, fg_color=BG_CARD,
                      corner_radius=0, border_color=BORDER, border_width=1)
topbar.pack(fill="x")
topbar.pack_propagate(False)
ctk.CTkLabel(topbar, text="Intelligent Campus Networking System",
             font=("Arial", 18, "bold"),
             text_color=TEXT_PRIMARY).pack(side="left", padx=22, pady=14)
pill = ctk.CTkFrame(topbar, fg_color="#0D2818", corner_radius=20)
pill.pack(side="right", padx=18, pady=14)
ctk.CTkLabel(pill, text="● ONLINE", font=("Arial", 11, "bold"),
             text_color=SUCCESS).pack(padx=12, pady=4)

# ── STATS ROW
stats_row = ctk.CTkFrame(main_frame, fg_color="transparent", height=72)
stats_row.pack(fill="x", padx=18, pady=(14, 0))
stats_row.pack_propagate(False)

def stat_widget(parent, label, fn, color):
    f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10,
                     border_color=BORDER, border_width=1)
    f.pack(side="left", padx=4, expand=True, fill="both")
    ctk.CTkLabel(f, text=label, font=("Arial", 9),
                 text_color=TEXT_MUTED).pack(pady=(7, 0))
    val = ctk.CTkLabel(f, text=fn(), font=("Arial", 18, "bold"),
                       text_color=color)
    val.pack(pady=(0, 7))
    return val

vs = stat_widget(stats_row, "STUDENTS",
                  lambda: str(len(network)), ACCENT)
vc = stat_widget(stats_row, "CONNECTIONS",
                  lambda: str(sum(len(v) for v in network.values()) // 2),
                  SUCCESS)
vd = stat_widget(stats_row, "DEPARTMENTS",
                  lambda: str(len(set(departments.values()))), WARNING)
vn = stat_widget(stats_row, "DENSITY",
                  lambda: f"{(2*(sum(len(v) for v in network.values())//2))/(len(network)*(len(network)-1)):.2f}"
                  if len(network) > 1 else "0.00", ACCENT2)

def refresh_stats():
    n = len(network)
    c = sum(len(v) for v in network.values()) // 2
    vs.configure(text=str(n)); vc.configure(text=str(c))
    vd.configure(text=str(len(set(departments.values()))))
    vn.configure(text=f"{(2*c)/(n*(n-1)):.2f}" if n > 1 else "0.00")
    app.after(3000, refresh_stats)

refresh_stats()

# ── TOOLBAR
toolbar = ctk.CTkFrame(main_frame, fg_color="transparent", height=44)
toolbar.pack(fill="x", padx=18, pady=(10, 0))
toolbar.pack_propagate(False)

btn_cards = ctk.CTkButton(
    toolbar, text="⊞  Cards",
    width=100, height=32, corner_radius=7,
    fg_color=ACCENT2, hover_color=ACCENT,
    text_color="white", font=("Arial", 12, "bold"),
    command=lambda: [show_cards_view(), render_cards()]
)
btn_cards.pack(side="left", padx=(0, 4))

btn_log = ctk.CTkButton(
    toolbar, text="☰  Log",
    width=90, height=32, corner_radius=7,
    fg_color="transparent", hover_color=BG_INNER,
    text_color=TEXT_MUTED, font=("Arial", 12, "bold"),
    command=show_log_view
)
btn_log.pack(side="left", padx=4)

ctk.CTkFrame(toolbar, width=1, height=28, fg_color=BORDER,
             corner_radius=0).pack(side="left", padx=8)

dept_var = ctk.StringVar(value="ALL")
dept_menu = ctk.CTkOptionMenu(
    toolbar, variable=dept_var,
    values=["ALL", "CS", "AI", "SE", "EE", "ME", "BBA", "DS", "IT"],
    width=95, height=32, corner_radius=7,
    fg_color=BG_INNER, button_color=BORDER,
    button_hover_color=ACCENT2,
    text_color=TEXT_PRIMARY, font=("Arial", 12),
    command=apply_filters
)
dept_menu.pack(side="left", padx=4)

search_var = ctk.StringVar()
search_var.trace_add("write", apply_filters)
search_entry = ctk.CTkEntry(
    toolbar, textvariable=search_var,
    placeholder_text="🔍  Search by name…",
    width=200, height=32, corner_radius=7,
    border_color=BORDER, fg_color=BG_INNER,
    text_color=TEXT_PRIMARY,
    placeholder_text_color=TEXT_MUTED,
    font=("Arial", 12)
)
search_entry.pack(side="left", padx=4)

# ── CONTENT ROW
content_row = ctk.CTkFrame(main_frame, fg_color="transparent")
content_row.pack(fill="both", expand=True, padx=0, pady=(8, 0))

cards_area = ctk.CTkFrame(content_row, fg_color="transparent")

cards_scroll = ctk.CTkScrollableFrame(cards_area, fg_color="transparent")
cards_scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

cards_grid = ctk.CTkFrame(cards_scroll, fg_color="transparent")
cards_grid.pack(fill="both", expand=True)

output_area = ctk.CTkFrame(content_row, fg_color="transparent")

hdr = ctk.CTkFrame(output_area, fg_color="transparent")
hdr.pack(fill="x", padx=4, pady=(0, 4))
ctk.CTkLabel(hdr, text="OUTPUT  /  ACTIVITY LOG",
             font=("Arial", 11, "bold"),
             text_color=TEXT_MUTED).pack(side="left")
ctk.CTkButton(hdr, text="Clear", width=60, height=24, corner_radius=6,
              fg_color=BG_INNER, hover_color=BORDER,
              text_color=TEXT_MUTED, font=("Arial", 10),
              command=lambda: output_box.delete("1.0", "end")
              ).pack(side="right")

out_frame = ctk.CTkFrame(output_area, fg_color=BG_CARD,
                          corner_radius=10, border_color=BORDER, border_width=1)
out_frame.pack(fill="both", expand=True)
output_box = ctk.CTkTextbox(out_frame, font=("Courier New", 13),
                             fg_color="transparent", text_color="#C9D1D9",
                             wrap="word")
output_box.pack(fill="both", expand=True, padx=8, pady=8)
output_box.insert("end",
    "\n   ╔══════════════════════════════════════╗\n"
    "   ║   CAMPUS NETWORK SYSTEM  v8.0       ║\n"
    "   ╚══════════════════════════════════════╝\n\n"
    "   Activity log appears here.\n\n"
    "   ────────────────────────────────────────\n\n"
)

# ── TOAST
toast_frame = ctk.CTkFrame(main_frame, corner_radius=8, fg_color=SUCCESS)
toast_lbl   = ctk.CTkLabel(toast_frame, text="",
                             font=("Arial", 12, "bold"), text_color="white")
toast_lbl.pack(padx=6, pady=6)
toast_frame.place_forget()

# =====================================================================
# START
# =====================================================================
load_data()
show_cards_view()
render_cards()
app.mainloop()