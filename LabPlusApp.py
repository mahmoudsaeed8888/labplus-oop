import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from LabRegister import TEST_TYPES, normalize_name

# ---------------- design tokens (navy / blue / lime green) ----------------
BG = "#eef3f9"        # page background
CARD = "#ffffff"      # card background
BORDER = "#dde6f0"
SHADOW = "#cfd9e6"
NAV = "#021a3f"       # navbar + hero (deep navy)
NAV_TEXT = "#c3d1e6"
PRIMARY = "#1e90e8"   # logo blue
PRIMARY_D = "#1477c8"
ACCENT = "#55b800"    # green buttons
ACCENT_D = "#459a00"
LIME = "#6fd400"      # bright green for text on navy
DANGER = "#dc2626"
DANGER_D = "#b91c1c"
TEXT = "#0b1f3a"
MUTED = "#5b6b82"
STRIPE = "#f6f9fd"
OK = "#2f8f00"
HIGH = "#b91c1c"
LOW = "#b45309"
PILL = "#e6f3fe"

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_SM = ("Segoe UI", 9)
FONT_XS = ("Segoe UI", 8, "bold")
FONT_H1 = ("Segoe UI", 22, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BRAND = ("Segoe UI", 16, "bold")

STATUS_ICON = {"Normal": "\u2713", "High": "\u25B2", "Low": "\u25BC"}


class LabPlusApp(tk.Tk):
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.pid = None        # selected patient
        self.rid = None        # selected result
        self._flash_job = None
        self.title("LabPlus - Kidney Lab Results")
        self.geometry("1240x800")
        self.minsize(1080, 700)
        self.configure(bg=BG)

        self._styles()
        self.status_var = tk.StringVar()

        # page layout: navbar / hero / main cards / explanation / footer
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=2)

        self._navbar()
        self._hero()

        main = tk.Frame(self, bg=BG)
        main.grid(row=2, column=0, sticky="nsew", padx=28, pady=(20, 12))
        main.columnconfigure(0, weight=1, uniform="cols")
        main.columnconfigure(1, weight=1, uniform="cols")
        main.rowconfigure(0, weight=1)

        self._patients_panel(main)
        self._results_panel(main)
        self._explain_panel()
        self._footer()

        self.refresh_patients()
        self.refresh_results()
        self._set_output("")
        self.protocol("WM_DELETE_WINDOW", self._close)

    # ---------------- styles ----------------
    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".", font=FONT, background=CARD, foreground=TEXT)

        # buttons
        base = dict(font=FONT_B, padding=(16, 8), borderwidth=0, focusthickness=0, relief="flat")
        s.configure("Primary.TButton", background=ACCENT, foreground="white", **base)
        s.map("Primary.TButton", background=[("active", ACCENT_D), ("pressed", ACCENT_D)])
        s.configure("Danger.TButton", background=DANGER, foreground="white", **base)
        s.map("Danger.TButton", background=[("active", DANGER_D), ("pressed", DANGER_D)])
        s.configure("Accent.TButton", background=PRIMARY, foreground="white", **base)
        s.map("Accent.TButton", background=[("active", PRIMARY_D), ("pressed", PRIMARY_D)])
        s.configure("Ghost.TButton", background="#e3f0fc", foreground=PRIMARY, **base)
        s.map("Ghost.TButton", background=[("active", "#cfe5f9"), ("pressed", "#cfe5f9")])

        # inputs
        s.configure("Web.TEntry", padding=8, fieldbackground="white", foreground=TEXT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, borderwidth=1)
        s.map("Web.TEntry", bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)],
              darkcolor=[("focus", PRIMARY)])
        s.configure("Web.TCombobox", padding=8, fieldbackground="white", background="white",
                    foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    arrowcolor=MUTED)
        s.map("Web.TCombobox", bordercolor=[("focus", PRIMARY)],
              fieldbackground=[("readonly", "white")], foreground=[("readonly", TEXT)])
        self.option_add("*TCombobox*Listbox.font", FONT)
        self.option_add("*TCombobox*Listbox.selectBackground", PRIMARY)
        self.option_add("*TCombobox*Listbox.selectForeground", "white")

        # tables
        s.configure("Web.Treeview", background="white", fieldbackground="white",
                    foreground=TEXT, rowheight=34, borderwidth=0, font=FONT)
        s.map("Web.Treeview", background=[("selected", "#d4ebff")],
              foreground=[("selected", TEXT)])
        s.configure("Web.Treeview.Heading", background="#e8f0f8", foreground=MUTED,
                    font=FONT_B, padding=(10, 9), relief="flat", borderwidth=0)
        s.map("Web.Treeview.Heading", background=[("active", "#d9e5f1")])

        # scrollbars
        s.configure("Vertical.TScrollbar", background="#c3d1e3", troughcolor=STRIPE,
                    bordercolor=STRIPE, arrowcolor=MUTED, relief="flat")

    # ---------------- small helpers ----------------
    def _card(self, parent, title, subtitle=""):
        """White card with a soft shadow and a header. Returns (outer, body)."""
        shadow = tk.Frame(parent, bg=SHADOW)
        outer = tk.Frame(shadow, bg=BORDER)
        outer.pack(fill="both", expand=True, pady=(0, 2))
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x", padx=20, pady=(16, 4))
        tk.Label(head, text=title, font=FONT_H2, bg=CARD, fg=TEXT).pack(side="left")
        if subtitle:
            tk.Label(head, text=subtitle, font=FONT_SM, bg=CARD, fg=MUTED).pack(side="left", padx=10)
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(8, 12))
        body = tk.Frame(inner, bg=CARD)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        return shadow, body

    def _field_label(self, parent, text):
        return tk.Label(parent, text=text.upper(), font=FONT_XS, bg=CARD, fg=MUTED)

    def _stat(self, parent, label, color):
        shadow = tk.Frame(parent, bg=SHADOW)
        box = tk.Frame(shadow, bg=BORDER)
        box.pack(pady=(0, 2))
        inner = tk.Frame(box, bg=CARD)
        inner.pack(padx=1, pady=1)
        tk.Frame(inner, bg=color, width=5).pack(side="left", fill="y")
        txt = tk.Frame(inner, bg=CARD)
        txt.pack(side="left", padx=(16, 18), pady=10)
        val = tk.Label(txt, text="0", font=("Segoe UI", 22, "bold"), bg=CARD, fg=TEXT,
                       width=4, anchor="w")
        val.pack(anchor="w")
        tk.Label(txt, text=label, font=FONT_SM, bg=CARD, fg=MUTED).pack(anchor="w")
        shadow.pack(side="left", padx=(12, 0))
        return val

    def _search_box(self, parent, var):
        """Search entry with a small magnifier icon drawn on a canvas."""
        row = tk.Frame(parent, bg=CARD)
        ic = tk.Canvas(row, width=20, height=20, bg=CARD, highlightthickness=0)
        ic.create_oval(3, 3, 13, 13, outline=MUTED, width=2)
        ic.create_line(12, 12, 17, 17, fill=MUTED, width=2)
        ic.pack(side="left", padx=(0, 8))
        ttk.Entry(row, textvariable=var, style="Web.TEntry").pack(
            side="left", fill="x", expand=True)
        return row

    def _flash(self, msg):
        """Short confirmation message in the footer."""
        self.status_var.set(msg)
        if self._flash_job:
            self.after_cancel(self._flash_job)
        self._flash_job = self.after(3500, lambda: self.status_var.set(""))

    # ---------------- navbar / hero / footer ----------------
    def _navbar(self):
        nav = tk.Frame(self, bg=NAV)
        nav.grid(row=0, column=0, sticky="ew")
        inner = tk.Frame(nav, bg=NAV)
        inner.pack(fill="x", padx=28, pady=12)

        # logo: blue + green leaves with a white plus
        logo = tk.Canvas(inner, width=42, height=38, bg=NAV, highlightthickness=0)
        logo.pack(side="left")
        logo.create_oval(2, 8, 28, 30, fill=PRIMARY, outline="")
        logo.create_oval(14, 6, 40, 28, fill=ACCENT, outline="")
        logo.create_line(21, 12, 21, 24, fill="white", width=3)
        logo.create_line(15, 18, 27, 18, fill="white", width=3)
        tk.Label(inner, text="lab", font=("Segoe UI", 18, "bold"), bg=NAV, fg=PRIMARY).pack(side="left", padx=(6, 0))
        tk.Label(inner, text="plus", font=("Segoe UI", 18, "bold"), bg=NAV, fg=LIME).pack(side="left")

        links = tk.Frame(inner, bg=NAV)
        links.pack(side="left", padx=40)
        for text, cmd in (("Dashboard", self._go_dashboard), ("Patients", self._go_patients),
                          ("Reports", self._go_reports), ("Help", self._help)):
            lb = tk.Label(links, text=text, font=FONT, bg=NAV, fg=NAV_TEXT, cursor="hand2")
            lb.pack(side="left", padx=14)
            lb.bind("<Enter>", lambda e, l=lb: l.config(fg="white"))
            lb.bind("<Leave>", lambda e, l=lb: l.config(fg=NAV_TEXT))
            lb.bind("<Button-1>", lambda e, c=cmd: c())

        # avatar circle on the right
        av = tk.Canvas(inner, width=38, height=38, bg=NAV, highlightthickness=0)
        av.pack(side="right")
        av.create_oval(2, 2, 36, 36, fill=ACCENT, outline="")
        av.create_text(19, 19, text="LP", fill="white", font=("Segoe UI", 10, "bold"))

        # thin accent line under the navbar
        tk.Frame(self, bg=LIME, height=2).grid(row=0, column=0, sticky="sew")

    def _hero(self):
        hero = tk.Frame(self, bg=NAV)
        hero.grid(row=1, column=0, sticky="ew")
        wrap = tk.Frame(hero, bg=NAV)
        wrap.pack(fill="x", padx=28, pady=(10, 28))

        left = tk.Frame(wrap, bg=NAV)
        left.pack(side="left")
        tk.Label(left, text="LabPlus kidney lab analysis \u2014 clear results, simple explanations",
                 font=("Segoe UI", 11, "bold"), bg=NAV, fg=LIME).pack(anchor="w")
        tk.Label(left, text="Kidney Lab Results", font=FONT_H1, bg=NAV, fg="white").pack(
            anchor="w", pady=(4, 0))
        tk.Label(left, text="Manage patients, record tests and get a clear explanation of every result.",
                 font=FONT, bg=NAV, fg=NAV_TEXT).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(wrap, bg=NAV)
        right.pack(side="right")
        self.st_patients = self._stat(right, "Patients", PRIMARY)
        self.st_results = self._stat(right, "Results (selected)", ACCENT)
        self.st_abnormal = self._stat(right, "Abnormal", DANGER)

    def _footer(self):
        foot = tk.Frame(self, bg=BG)
        foot.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 12))
        tk.Label(foot, text="\u00A9 LabPlus \u00B7 Kidney lab results analysis \u00B7 "
                            "For information only, not a medical diagnosis",
                 font=FONT_SM, bg=BG, fg=MUTED).pack(side="left")
        tk.Label(foot, textvariable=self.status_var, font=FONT_B, bg=BG, fg=OK).pack(side="right")

    def _help(self):
        messagebox.showinfo(
            "Help",
            "1. Add a patient (name, age, sex).\n"
            "2. Select the patient from the list.\n"
            "3. Add lab results (test, value, date).\n"
            "4. Click 'Explain results' to read the explanation.\n\n"
            "Tip: press Enter inside a form to add (or update) quickly.")

    # navbar shortcuts
    def _go_dashboard(self):
        self.psearch.set("")
        self.rsearch.set("")
        self.clear_patient()

    def _go_patients(self):
        self.name_entry.focus_set()

    def _go_reports(self):
        self.explain()

    def _update_stats(self):
        self.st_patients.config(text=str(len(self.system.search_patients(""))))
        if self.pid is None:
            self.st_results.config(text="-")
            self.st_abnormal.config(text="-", fg=TEXT)
            return
        p = self.system.get_patient(self.pid)
        bad = sum(1 for r in p.results if r.status(p.sex) != "Normal")
        self.st_results.config(text=str(len(p.results)))
        self.st_abnormal.config(text=str(bad), fg=DANGER if bad else TEXT)

    # ---------------- table helper ----------------
    def _table(self, parent, columns, headings, widths, stretch, empty_text):
        """Bordered Treeview with scrollbar and an 'empty' message. Returns (tree, empty_label)."""
        wrap = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(wrap, bg="white")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tree = ttk.Treeview(inner, columns=columns, show="headings", selectmode="browse",
                            height=6, style="Web.Treeview")
        for c, h, w, st in zip(columns, headings, widths, stretch):
            tree.heading(c, text=h, anchor="w")
            tree.column(c, width=w, minwidth=30, anchor="w", stretch=st)
        tree.tag_configure("odd", background=STRIPE)
        sb = ttk.Scrollbar(inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        empty = tk.Label(inner, text=empty_text, font=FONT, bg="white", fg=MUTED)
        return wrap, tree, empty

    def _show_empty(self, label, text=None):
        if text is not None:
            label.config(text=text)
        label.place(relx=0.5, rely=0.58, anchor="center")
        label.lift()

    # ---------------- patients panel (left) ----------------
    def _patients_panel(self, parent):
        outer, box = self._card(parent, "Patients", "Add and manage patient records")
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        box.rowconfigure(3, weight=1)
        box.columnconfigure(0, weight=1)

        form = tk.Frame(box, bg=CARD)
        form.grid(row=0, column=0, sticky="ew")
        form.columnconfigure(0, weight=3)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        self.pv = {k: tk.StringVar() for k in ("name", "age", "sex")}
        self.pv["sex"].set("Male")

        self._field_label(form, "Full name").grid(row=0, column=0, sticky="w")
        self._field_label(form, "Age").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self._field_label(form, "Sex").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.name_entry = ttk.Entry(form, textvariable=self.pv["name"], style="Web.TEntry")
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        age_entry = ttk.Entry(form, textvariable=self.pv["age"], style="Web.TEntry", width=6)
        age_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 0))
        ttk.Combobox(form, textvariable=self.pv["sex"], values=["Male", "Female"],
                     state="readonly", style="Web.TCombobox", width=8).grid(
            row=1, column=2, sticky="ew", padx=(10, 0), pady=(3, 0))
        for w in (self.name_entry, age_entry):
            w.bind("<Return>", lambda e: self._submit_patient())

        btns = tk.Frame(box, bg=CARD)
        btns.grid(row=1, column=0, sticky="w", pady=14)
        for t, c, st in (("\uFF0B Add", self.add_patient, "Primary.TButton"),
                         ("Update", self.update_patient, "Ghost.TButton"),
                         ("Delete", self.delete_patient, "Danger.TButton"),
                         ("Clear", self.clear_patient, "Ghost.TButton")):
            ttk.Button(btns, text=t, command=c, style=st, cursor="hand2").pack(side="left", padx=(0, 8))

        self.psearch = tk.StringVar()
        self.psearch.trace_add("write", lambda *a: self.refresh_patients())
        self._search_box(box, self.psearch).grid(row=2, column=0, sticky="ew", pady=(0, 10))

        wrap, self.ptree, self.p_empty = self._table(
            box, ("id", "name", "age", "sex", "n"), ("ID", "Name", "Age", "Sex", "Results"),
            (45, 190, 55, 75, 70), (False, True, False, False, False),
            "No patients yet \u2014 add one above")
        wrap.grid(row=3, column=0, sticky="nsew")
        self.ptree.bind("<<TreeviewSelect>>", self.on_patient_select)

    def _submit_patient(self):
        if self.pid is None:
            self.add_patient()
        else:
            self.update_patient()

    def refresh_patients(self):
        self.ptree.delete(*self.ptree.get_children())
        rows = self.system.search_patients(self.psearch.get())
        for i, p in enumerate(rows):
            self.ptree.insert("", "end", iid=str(p.id), tags=("odd",) if i % 2 else (),
                              values=(p.id, p.name, p.age, p.sex, len(p.results)))
        if rows:
            self.p_empty.place_forget()
        elif self.psearch.get().strip():
            self._show_empty(self.p_empty, "No patients match your search")
        else:
            self._show_empty(self.p_empty, "No patients yet \u2014 add one above")
        self._update_stats()

    def clear_patient(self):
        self.pid = None
        self._clear_result_form()
        for k in ("name", "age"):
            self.pv[k].set("")
        self.ptree.selection_remove(self.ptree.selection())
        self.patient_lbl.config(text="Select a patient from the list", fg=MUTED)
        self._set_output("")
        self.refresh_results()

    def on_patient_select(self, _e):
        sel = self.ptree.selection()
        if not sel:
            return
        p = self.system.get_patient(int(sel[0]))
        self.pid = p.id
        self._clear_result_form()
        self.pv["name"].set(p.name)
        self.pv["age"].set(p.age)
        self.pv["sex"].set(p.sex)
        self.patient_lbl.config(text=f"{p.name}  \u00B7  {p.sex}, {p.age}", fg=TEXT)
        self._set_output("")
        self.refresh_results()

    def add_patient(self):
        try:
            self.system.add_patient(*(self.pv[k].get() for k in ("name", "age", "sex")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        self.clear_patient()
        self.refresh_patients()
        self._flash("\u2713 Patient added")

    def update_patient(self):
        if self.pid is None:
            return messagebox.showinfo("Update", "Select a patient first.")
        try:
            self.system.update_patient(self.pid, *(self.pv[k].get() for k in ("name", "age", "sex")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        p = self.system.get_patient(self.pid)
        self.patient_lbl.config(text=f"{p.name}  \u00B7  {p.sex}, {p.age}", fg=TEXT)
        self.refresh_patients()
        self.refresh_results()
        self._flash("\u2713 Patient updated")

    def delete_patient(self):
        if self.pid is None:
            return messagebox.showinfo("Delete", "Select a patient first.")
        if messagebox.askyesno("Confirm", "Delete this patient and all their results?"):
            self.system.delete_patient(self.pid)
            self.clear_patient()
            self.refresh_patients()
            self._flash("\u2713 Patient deleted")

    # ---------------- results panel (right) ----------------
    def _results_panel(self, parent):
        outer, box = self._card(parent, "Lab Results", "Record and review tests")
        outer.grid(row=0, column=1, sticky="nsew", padx=(9, 0))
        box.rowconfigure(4, weight=1)
        box.columnconfigure(0, weight=1)

        # patient "pill"
        pill = tk.Frame(box, bg=PILL)
        pill.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        tk.Label(pill, text="PATIENT", font=FONT_XS, bg=PILL,
                 fg=PRIMARY).pack(side="left", padx=(14, 10), pady=9)
        self.patient_lbl = tk.Label(pill, text="Select a patient from the list",
                                    font=FONT_B, bg=PILL, fg=MUTED)
        self.patient_lbl.pack(side="left")

        form = tk.Frame(box, bg=CARD)
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=2)
        self.rv = {k: tk.StringVar() for k in ("test", "value", "date")}
        self.rv["date"].set(date.today().isoformat())

        self._field_label(form, "Test (e.g. Cr, BUN, Hb, K)").grid(row=0, column=0, sticky="w")
        self.value_lbl = self._field_label(form, "Value")
        self.value_lbl.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self._field_label(form, "Date").grid(row=0, column=2, sticky="w", padx=(10, 0))
        test_cb = ttk.Combobox(form, textvariable=self.rv["test"], values=list(TEST_TYPES),
                               style="Web.TCombobox", width=14)
        test_cb.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        value_entry = ttk.Entry(form, textvariable=self.rv["value"], style="Web.TEntry", width=9)
        value_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(3, 0))
        date_entry = ttk.Entry(form, textvariable=self.rv["date"], style="Web.TEntry", width=14)
        date_entry.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(3, 0))
        for w in (value_entry, date_entry):
            w.bind("<Return>", lambda e: self._submit_result())
        # show the unit next to "Value" once a known test is chosen
        self.rv["test"].trace_add("write", lambda *a: self._update_unit_hint())

        btns = tk.Frame(box, bg=CARD)
        btns.grid(row=2, column=0, sticky="w", pady=14)
        for t, c, st in (("\uFF0B Add", self.add_result, "Primary.TButton"),
                         ("Update", self.update_result, "Ghost.TButton"),
                         ("Delete", self.delete_result, "Danger.TButton"),
                         ("Explain results", self.explain, "Accent.TButton")):
            ttk.Button(btns, text=t, command=c, style=st, cursor="hand2").pack(side="left", padx=(0, 8))

        self.rsearch = tk.StringVar()
        self.rsearch.trace_add("write", lambda *a: self.refresh_results())
        self._search_box(box, self.rsearch).grid(row=3, column=0, sticky="ew", pady=(0, 10))

        wrap, self.rtree, self.r_empty = self._table(
            box, ("id", "date", "test", "value", "range", "status"),
            ("ID", "Date", "Test", "Value", "Normal range", "Status"),
            (40, 90, 100, 100, 100, 90), (False, False, True, False, False, False),
            "Select a patient to see results")
        wrap.grid(row=4, column=0, sticky="nsew")
        self.rtree.tag_configure("ok", foreground=OK)
        self.rtree.tag_configure("high", foreground=HIGH)
        self.rtree.tag_configure("low", foreground=LOW)
        self.rtree.bind("<<TreeviewSelect>>", self.on_result_select)

    def _update_unit_hint(self):
        try:
            unit = TEST_TYPES[normalize_name(self.rv["test"].get())].UNIT
            self.value_lbl.config(text=f"VALUE \u00B7 {unit}")
        except ValueError:
            self.value_lbl.config(text="VALUE")

    def _submit_result(self):
        if self.rid is None:
            self.add_result()
        else:
            self.update_result()

    def refresh_results(self):
        self.rtree.delete(*self.rtree.get_children())
        if self.pid is None:
            self._show_empty(self.r_empty, "Select a patient to see results")
            self._update_stats()
            return
        sex = self.system.get_patient(self.pid).sex
        rows = self.system.search_results(self.pid, self.rsearch.get())
        for i, r in enumerate(rows):
            lo, hi = r.reference_range(sex)   # polymorphism
            st = r.status(sex)
            tag = {"Normal": "ok", "High": "high", "Low": "low"}[st]
            tags = (tag,) + (("odd",) if i % 2 else ())
            self.rtree.insert("", "end", iid=str(r.id), tags=tags,
                              values=(r.id, r.date, r.name, f"{r.value:g} {r.unit}",
                                      f"{lo:g} - {hi:g}", f"{STATUS_ICON[st]} {st}"))
        if rows:
            self.r_empty.place_forget()
        elif self.rsearch.get().strip():
            self._show_empty(self.r_empty, "No results match your search")
        else:
            self._show_empty(self.r_empty, "No results yet \u2014 add the first test above")
        self._update_stats()

    def on_result_select(self, _e):
        sel = self.rtree.selection()
        if not sel or self.pid is None:
            return
        self.rid = int(sel[0])
        r = next(x for x in self.system.get_patient(self.pid).results if x.id == self.rid)
        self.rv["test"].set(r.name)
        self.rv["value"].set(f"{r.value:g}")
        self.rv["date"].set(r.date)

    def _clear_result_form(self):
        self.rid = None
        self.rv["test"].set("")
        self.rv["value"].set("")
        self.rv["date"].set(date.today().isoformat())
        self.rtree.selection_remove(self.rtree.selection())

    def _need_patient(self):
        if self.pid is None:
            messagebox.showinfo("LabPlus", "Select a patient from the list first.")
            return False
        return True

    def add_result(self):
        if not self._need_patient():
            return
        try:
            self.system.add_result(self.pid, *(self.rv[k].get() for k in ("test", "value", "date")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        self.refresh_results()
        self.refresh_patients()
        self._clear_result_form()
        self.ptree.selection_set(str(self.pid))   # keep the patient selected
        self._flash("\u2713 Result added")

    def update_result(self):
        if not self._need_patient():
            return
        if self.rid is None:
            return messagebox.showinfo("Update", "Select a result in the table first.")
        try:
            self.system.update_result(self.pid, self.rid,
                                      *(self.rv[k].get() for k in ("test", "value", "date")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        self.refresh_results()
        self._clear_result_form()
        self._flash("\u2713 Result updated")

    def delete_result(self):
        if not self._need_patient():
            return
        if self.rid is None:
            return messagebox.showinfo("Delete", "Select a result in the table first.")
        if messagebox.askyesno("Confirm", "Delete this result?"):
            self.system.delete_result(self.pid, self.rid)
            self._clear_result_form()
            self.refresh_results()
            self.refresh_patients()
            self.ptree.selection_set(str(self.pid))
            self._flash("\u2713 Result deleted")

    # ---------------- explanation panel (bottom) ----------------
    def _explain_panel(self):
        outer, box = self._card(self, "Explanation", "Plain-language summary of the selected patient's results")
        outer.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 12))
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        self.out = tk.Text(box, height=8, wrap="word", state="disabled", font=("Segoe UI", 10),
                           bg="#f8fafc", fg=TEXT, relief="flat", padx=16, pady=12,
                           highlightthickness=1, highlightbackground=BORDER,
                           highlightcolor=BORDER, spacing1=2, spacing3=4, cursor="arrow")
        self.out.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(box, orient="vertical", command=self.out.yview)
        self.out.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        o = self.out
        o.tag_configure("h", font=("Segoe UI", 13, "bold"), foreground=TEXT, spacing3=8)
        o.tag_configure("name", font=("Segoe UI", 10, "bold"), foreground=TEXT, spacing1=6)
        o.tag_configure("val", foreground=TEXT, spacing1=6)
        o.tag_configure("rng", foreground=MUTED, spacing1=6)
        o.tag_configure("Normal", foreground=OK, font=("Segoe UI", 10, "bold"), spacing1=6)
        o.tag_configure("High", foreground=HIGH, font=("Segoe UI", 10, "bold"), spacing1=6)
        o.tag_configure("Low", foreground=LOW, font=("Segoe UI", 10, "bold"), spacing1=6)
        o.tag_configure("advice", foreground="#475569", lmargin1=30, lmargin2=30)
        o.tag_configure("trend_good", foreground=OK, lmargin1=30, lmargin2=30)
        o.tag_configure("trend_bad", foreground=HIGH, lmargin1=30, lmargin2=30)
        o.tag_configure("trend", foreground=MUTED, lmargin1=30, lmargin2=30)
        o.tag_configure("warn", foreground="#92400e", background="#fef3c7",
                        font=("Segoe UI", 9, "bold"), spacing1=12, lmargin1=8, lmargin2=8)
        o.tag_configure("hint", foreground=MUTED, font=("Segoe UI", 10, "italic"))

    _LINE = re.compile(r"^- (.+?): (.+?) \((Low|High|Normal), (normal .+)\)$")

    def _set_output(self, text):
        o = self.out
        o.config(state="normal")
        o.delete("1.0", "end")
        text = text or ""
        if not text.strip():
            o.insert("end", "Select a patient, then click \u201CExplain results\u201D "
                            "to see a summary here.", "hint")
        elif text.startswith("No results"):
            o.insert("end", text, "hint")
        else:
            for line in text.split("\n"):
                self._render_line(line)
        o.config(state="disabled")

    def _render_line(self, line):
        o = self.out
        m = self._LINE.match(line)
        if line.startswith("Summary for"):
            o.insert("end", line + "\n", "h")
        elif m:
            name, value, st, rng = m.groups()
            o.insert("end", f"{STATUS_ICON[st]}  ", st)
            o.insert("end", name, "name")
            o.insert("end", f"   {value}   ", "val")
            o.insert("end", st, st)
            o.insert("end", f"   ({rng})\n", "rng")
        elif line.strip().startswith("Trend:"):
            low = line.lower()
            tag = "trend_good" if ("improved" in low or "stable" in low) else \
                  "trend_bad" if "worse" in low else "trend"
            o.insert("end", "\u21AA " + line.strip() + "\n", tag)
        elif "NOT a medical diagnosis" in line:
            o.insert("end", "\u26A0  " + line.strip() + "\n", "warn")
        elif line.startswith("    "):
            o.insert("end", line.strip() + "\n", "advice")
        elif line.strip():
            o.insert("end", line + "\n")

    def explain(self):
        if not self._need_patient():
            return
        self._set_output(self.system.explain(self.pid))

    def _close(self):
        self.system.save()
        self.destroy()