import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from LabRegister import TEST_TYPES

# ---------------- design tokens (website-like palette) ----------------
BG = "#f3f5f9"        # page background
CARD = "#ffffff"      # card background
BORDER = "#e5e7eb"
NAV = "#0f172a"       # navbar
NAV_TEXT = "#cbd5e1"
PRIMARY = "#2563eb"
PRIMARY_D = "#1d4ed8"
ACCENT = "#14b8a6"
DANGER = "#dc2626"
DANGER_D = "#b91c1c"
TEXT = "#1f2937"
MUTED = "#6b7280"
STRIPE = "#f9fafb"
OK = "#15803d"
BAD = "#b91c1c"

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_SM = ("Segoe UI", 9)
FONT_H1 = ("Segoe UI", 20, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BRAND = ("Segoe UI", 16, "bold")


class LabPlusApp(tk.Tk):
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.pid = None        # selected patient
        self.rid = None        # selected result
        self.title("LabPlus - Kidney Lab Results")
        self.geometry("1200x780")
        self.minsize(1050, 680)
        self.configure(bg=BG)

        self._styles()

        # page layout: navbar / hero / main cards / explanation / footer
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=2)

        self._navbar()
        self._hero()

        main = tk.Frame(self, bg=BG)
        main.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 10))
        main.columnconfigure(0, weight=1, uniform="cols")
        main.columnconfigure(1, weight=1, uniform="cols")
        main.rowconfigure(0, weight=1)

        self._patients_panel(main)
        self._results_panel(main)
        self._explain_panel()
        self._footer()

        self.refresh_patients()
        self.protocol("WM_DELETE_WINDOW", self._close)

    # ---------------- styles ----------------
    def _styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(".", font=FONT, background=CARD, foreground=TEXT)

        # buttons
        base = dict(font=FONT_B, padding=(14, 7), borderwidth=0, focusthickness=0, relief="flat")
        s.configure("Primary.TButton", background=PRIMARY, foreground="white", **base)
        s.map("Primary.TButton", background=[("active", PRIMARY_D), ("pressed", PRIMARY_D)])
        s.configure("Danger.TButton", background=DANGER, foreground="white", **base)
        s.map("Danger.TButton", background=[("active", DANGER_D), ("pressed", DANGER_D)])
        s.configure("Accent.TButton", background=ACCENT, foreground="white", **base)
        s.map("Accent.TButton", background=[("active", "#0d9488"), ("pressed", "#0d9488")])
        s.configure("Ghost.TButton", background="#eef2ff", foreground=PRIMARY, **base)
        s.map("Ghost.TButton", background=[("active", "#e0e7ff"), ("pressed", "#e0e7ff")])

        # inputs
        s.configure("Web.TEntry", padding=7, fieldbackground="white", foreground=TEXT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, borderwidth=1)
        s.map("Web.TEntry", bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)],
              darkcolor=[("focus", PRIMARY)])
        s.configure("Web.TCombobox", padding=7, fieldbackground="white", background="white",
                    foreground=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    arrowcolor=MUTED)
        s.map("Web.TCombobox", bordercolor=[("focus", PRIMARY)],
              fieldbackground=[("readonly", "white")], foreground=[("readonly", TEXT)])

        # tables
        s.configure("Web.Treeview", background="white", fieldbackground="white",
                    foreground=TEXT, rowheight=32, borderwidth=0, font=FONT)
        s.map("Web.Treeview", background=[("selected", "#dbeafe")],
              foreground=[("selected", TEXT)])
        s.configure("Web.Treeview.Heading", background="#f1f5f9", foreground=MUTED,
                    font=FONT_B, padding=(8, 8), relief="flat", borderwidth=0)
        s.map("Web.Treeview.Heading", background=[("active", "#e2e8f0")])

        # scrollbars
        s.configure("Vertical.TScrollbar", background="#cbd5e1", troughcolor=STRIPE,
                    bordercolor=STRIPE, arrowcolor=MUTED, relief="flat")

    # ---------------- small helpers ----------------
    def _card(self, parent, title, subtitle=""):
        """White card with a thin border and a header. Returns (outer, body)."""
        outer = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x", padx=18, pady=(14, 4))
        tk.Label(head, text=title, font=FONT_H2, bg=CARD, fg=TEXT).pack(side="left")
        if subtitle:
            tk.Label(head, text=subtitle, font=FONT_SM, bg=CARD, fg=MUTED).pack(side="left", padx=10)
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(6, 10))
        body = tk.Frame(inner, bg=CARD)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        return outer, body

    def _field_label(self, parent, text):
        return tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
                        bg=CARD, fg=MUTED)

    def _stat(self, parent, label, color):
        box = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(box, bg=CARD)
        inner.pack(padx=1, pady=1)
        tk.Frame(inner, bg=color, width=4).pack(side="left", fill="y")
        txt = tk.Frame(inner, bg=CARD)
        txt.pack(side="left", padx=14, pady=8)
        val = tk.Label(txt, text="0", font=("Segoe UI", 18, "bold"), bg=CARD, fg=TEXT)
        val.pack(anchor="w")
        tk.Label(txt, text=label, font=FONT_SM, bg=CARD, fg=MUTED).pack(anchor="w")
        box.pack(side="left", padx=(10, 0))
        return val

    # ---------------- navbar / hero / footer ----------------
    def _navbar(self):
        nav = tk.Frame(self, bg=NAV)
        nav.grid(row=0, column=0, sticky="ew")
        inner = tk.Frame(nav, bg=NAV)
        inner.pack(fill="x", padx=24, pady=12)

        tk.Label(inner, text="🧪", font=("Segoe UI", 16), bg=NAV, fg="white").pack(side="left")
        tk.Label(inner, text="Lab", font=FONT_BRAND, bg=NAV, fg="white").pack(side="left", padx=(6, 0))
        tk.Label(inner, text="Plus", font=FONT_BRAND, bg=NAV, fg=ACCENT).pack(side="left")

        links = tk.Frame(inner, bg=NAV)
        links.pack(side="left", padx=40)
        for text, cmd in (("Dashboard", None), ("Patients", None), ("Reports", None),
                          ("Help", self._help)):
            lb = tk.Label(links, text=text, font=FONT, bg=NAV, fg=NAV_TEXT, cursor="hand2")
            lb.pack(side="left", padx=14)
            lb.bind("<Enter>", lambda e, l=lb: l.config(fg="white"))
            lb.bind("<Leave>", lambda e, l=lb: l.config(fg=NAV_TEXT))
            if cmd:
                lb.bind("<Button-1>", lambda e, c=cmd: c())

        # avatar circle on the right
        av = tk.Canvas(inner, width=36, height=36, bg=NAV, highlightthickness=0)
        av.pack(side="right")
        av.create_oval(2, 2, 34, 34, fill=PRIMARY, outline="")
        av.create_text(18, 18, text="LP", fill="white", font=("Segoe UI", 10, "bold"))

    def _hero(self):
        hero = tk.Frame(self, bg=BG)
        hero.grid(row=1, column=0, sticky="ew", padx=24, pady=(18, 14))

        left = tk.Frame(hero, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="Kidney Lab Results", font=FONT_H1, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(left, text="Manage patients, record tests and get a clear explanation of every result.",
                 font=FONT, bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(hero, bg=BG)
        right.pack(side="right")
        self.st_patients = self._stat(right, "Patients", PRIMARY)
        self.st_results = self._stat(right, "Results (selected)", ACCENT)
        self.st_abnormal = self._stat(right, "Abnormal", DANGER)

    def _footer(self):
        foot = tk.Frame(self, bg=BG)
        foot.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 10))
        tk.Label(foot, text="© LabPlus · Kidney lab results analysis · "
                            "For information only, not a medical diagnosis",
                 font=FONT_SM, bg=BG, fg=MUTED).pack(side="left")

    def _help(self):
        messagebox.showinfo(
            "Help",
            "1. Add a patient (name, age, sex).\n"
            "2. Select the patient from the list.\n"
            "3. Add lab results (test, value, date).\n"
            "4. Click 'Explain results' to read the explanation.")

    def _update_stats(self):
        self.st_patients.config(text=str(len(self.system.search_patients(""))))
        if self.pid is None:
            self.st_results.config(text="-")
            self.st_abnormal.config(text="-")
            return
        p = self.system.get_patient(self.pid)
        bad = sum(1 for r in p.results if r.status(p.sex) != "Normal")
        self.st_results.config(text=str(len(p.results)))
        self.st_abnormal.config(text=str(bad), fg=DANGER if bad else TEXT)

    # ---------------- patients panel (left) ----------------
    def _patients_panel(self, parent):
        outer, box = self._card(parent, "Patients", "Add and manage patient records")
        outer.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
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
        self._field_label(form, "Age").grid(row=0, column=1, sticky="w", padx=(8, 0))
        self._field_label(form, "Sex").grid(row=0, column=2, sticky="w", padx=(8, 0))
        ttk.Entry(form, textvariable=self.pv["name"], style="Web.TEntry").grid(
            row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Entry(form, textvariable=self.pv["age"], style="Web.TEntry", width=6).grid(
            row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 0))
        ttk.Combobox(form, textvariable=self.pv["sex"], values=["Male", "Female"],
                     state="readonly", style="Web.TCombobox", width=8).grid(
            row=1, column=2, sticky="ew", padx=(8, 0), pady=(2, 0))

        btns = tk.Frame(box, bg=CARD)
        btns.grid(row=1, column=0, sticky="w", pady=12)
        for t, c, st in (("＋ Add", self.add_patient, "Primary.TButton"),
                         ("Update", self.update_patient, "Ghost.TButton"),
                         ("Delete", self.delete_patient, "Danger.TButton"),
                         ("Clear", self.clear_patient, "Ghost.TButton")):
            ttk.Button(btns, text=t, command=c, style=st, cursor="hand2").pack(side="left", padx=(0, 8))

        s = tk.Frame(box, bg=CARD)
        s.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        tk.Label(s, text="🔍", bg=CARD, fg=MUTED).pack(side="left", padx=(0, 6))
        self.psearch = tk.StringVar()
        self.psearch.trace_add("write", lambda *a: self.refresh_patients())
        ttk.Entry(s, textvariable=self.psearch, style="Web.TEntry").pack(
            side="left", fill="x", expand=True)

        wrap = tk.Frame(box, bg=BORDER)
        wrap.grid(row=3, column=0, sticky="nsew")
        inner = tk.Frame(wrap, bg="white")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self.ptree = ttk.Treeview(inner, columns=("id", "name", "age", "sex", "n"),
                                  show="headings", selectmode="browse", height=6,
                                  style="Web.Treeview")
        for c, h, w in (("id", "ID", 40), ("name", "Name", 180), ("age", "Age", 50),
                        ("sex", "Sex", 70), ("n", "Results", 60)):
            self.ptree.heading(c, text=h, anchor="w")
            self.ptree.column(c, width=w, anchor="w")
        self.ptree.tag_configure("odd", background=STRIPE)
        sb = ttk.Scrollbar(inner, orient="vertical", command=self.ptree.yview)
        self.ptree.configure(yscrollcommand=sb.set)
        self.ptree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.ptree.bind("<<TreeviewSelect>>", self.on_patient_select)

    def refresh_patients(self):
        self.ptree.delete(*self.ptree.get_children())
        for i, p in enumerate(self.system.search_patients(self.psearch.get())):
            self.ptree.insert("", "end", iid=str(p.id), tags=("odd",) if i % 2 else (),
                              values=(p.id, p.name, p.age, p.sex, len(p.results)))
        self._update_stats()

    def clear_patient(self):
        self.pid = None
        self._clear_result_form()
        for k in ("name", "age"):
            self.pv[k].set("")
        self.ptree.selection_remove(self.ptree.selection())
        self.patient_lbl.config(text="Select a patient from the list")
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
        self.patient_lbl.config(text=f"{p.name}  ·  {p.sex}, {p.age}")
        self._set_output("")
        self.refresh_results()

    def add_patient(self):
        try:
            self.system.add_patient(*(self.pv[k].get() for k in ("name", "age", "sex")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        self.clear_patient()
        self.refresh_patients()

    def update_patient(self):
        if self.pid is None:
            return messagebox.showinfo("Update", "Select a patient first.")
        try:
            self.system.update_patient(self.pid, *(self.pv[k].get() for k in ("name", "age", "sex")))
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        p = self.system.get_patient(self.pid)
        self.patient_lbl.config(text=f"{p.name}  ·  {p.sex}, {p.age}")
        self.refresh_patients()
        self.refresh_results()

    def delete_patient(self):
        if self.pid is None:
            return messagebox.showinfo("Delete", "Select a patient first.")
        if messagebox.askyesno("Confirm", "Delete this patient and all their results?"):
            self.system.delete_patient(self.pid)
            self.clear_patient()
            self.refresh_patients()

    # ---------------- results panel (right) ----------------
    def _results_panel(self, parent):
        outer, box = self._card(parent, "Lab Results", "Record and review tests")
        outer.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        box.rowconfigure(4, weight=1)
        box.columnconfigure(0, weight=1)

        # patient "pill"
        pill = tk.Frame(box, bg="#eff6ff")
        pill.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(pill, text="PATIENT", font=("Segoe UI", 8, "bold"), bg="#eff6ff",
                 fg=PRIMARY).pack(side="left", padx=(12, 8), pady=8)
        self.patient_lbl = tk.Label(pill, text="Select a patient from the list",
                                    font=FONT_B, bg="#eff6ff", fg=TEXT)
        self.patient_lbl.pack(side="left")

        form = tk.Frame(box, bg=CARD)
        form.grid(row=1, column=0, sticky="ew")
        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=2)
        self.rv = {k: tk.StringVar() for k in ("test", "value", "date")}
        self.rv["date"].set(date.today().isoformat())

        self._field_label(form, "Test (e.g. Cr, BUN, Hb, K)").grid(row=0, column=0, sticky="w")
        self._field_label(form, "Value").grid(row=0, column=1, sticky="w", padx=(8, 0))
        self._field_label(form, "Date").grid(row=0, column=2, sticky="w", padx=(8, 0))
        ttk.Combobox(form, textvariable=self.rv["test"], values=list(TEST_TYPES),
                     style="Web.TCombobox", width=14).grid(row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Entry(form, textvariable=self.rv["value"], style="Web.TEntry", width=9).grid(
            row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 0))
        ttk.Entry(form, textvariable=self.rv["date"], style="Web.TEntry", width=14).grid(
            row=1, column=2, sticky="ew", padx=(8, 0), pady=(2, 0))

        btns = tk.Frame(box, bg=CARD)
        btns.grid(row=2, column=0, sticky="w", pady=12)
        for t, c, st in (("＋ Add", self.add_result, "Primary.TButton"),
                         ("Update", self.update_result, "Ghost.TButton"),
                         ("Delete", self.delete_result, "Danger.TButton"),
                         ("Explain results", self.explain, "Accent.TButton")):
            ttk.Button(btns, text=t, command=c, style=st, cursor="hand2").pack(side="left", padx=(0, 8))

        s = tk.Frame(box, bg=CARD)
        s.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        tk.Label(s, text="🔍", bg=CARD, fg=MUTED).pack(side="left", padx=(0, 6))
        self.rsearch = tk.StringVar()
        self.rsearch.trace_add("write", lambda *a: self.refresh_results())
        ttk.Entry(s, textvariable=self.rsearch, style="Web.TEntry").pack(
            side="left", fill="x", expand=True)

        wrap = tk.Frame(box, bg=BORDER)
        wrap.grid(row=4, column=0, sticky="nsew")
        inner = tk.Frame(wrap, bg="white")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        cols = ("id", "date", "test", "value", "range", "status")
        self.rtree = ttk.Treeview(inner, columns=cols, show="headings",
                                  selectmode="browse", height=6, style="Web.Treeview")
        for c, h, w in zip(cols, ("ID", "Date", "Test", "Value", "Normal range", "Status"),
                           (35, 85, 95, 95, 90, 85)):
            self.rtree.heading(c, text=h, anchor="w")
            self.rtree.column(c, width=w, anchor="w")
        self.rtree.tag_configure("odd", background=STRIPE)
        self.rtree.tag_configure("ok", foreground=OK)
        self.rtree.tag_configure("bad", foreground=BAD)
        sb = ttk.Scrollbar(inner, orient="vertical", command=self.rtree.yview)
        self.rtree.configure(yscrollcommand=sb.set)
        self.rtree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.rtree.bind("<<TreeviewSelect>>", self.on_result_select)

    def refresh_results(self):
        self.rtree.delete(*self.rtree.get_children())
        if self.pid is None:
            self._update_stats()
            return
        sex = self.system.get_patient(self.pid).sex
        for i, r in enumerate(self.system.search_results(self.pid, self.rsearch.get())):
            lo, hi = r.reference_range(sex)   # polymorphism
            st = r.status(sex)
            tags = ("ok" if st == "Normal" else "bad",) + (("odd",) if i % 2 else ())
            self.rtree.insert("", "end", iid=str(r.id), tags=tags,
                              values=(r.id, r.date, r.name, f"{r.value:g} {r.unit}",
                                      f"{lo:g} - {hi:g}", f"● {st}"))
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

    # ---------------- explanation panel (bottom) ----------------
    def _explain_panel(self):
        outer, box = self._card(self, "Explanation", "Plain-language summary of the selected patient's results")
        outer.grid(row=3, column=0, sticky="nsew", padx=24, pady=(0, 10))
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        self.out = tk.Text(box, height=8, wrap="word", state="disabled", font=("Segoe UI", 10),
                           bg="#f8fafc", fg=TEXT, relief="flat", padx=14, pady=10,
                           highlightthickness=1, highlightbackground=BORDER,
                           highlightcolor=BORDER, spacing3=4)
        self.out.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(box, orient="vertical", command=self.out.yview)
        self.out.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    def _set_output(self, text):
        self.out.config(state="normal")
        self.out.delete("1.0", "end")
        self.out.insert("end", text)
        self.out.config(state="disabled")

    def explain(self):
        if not self._need_patient():
            return
        self._set_output(self.system.explain(self.pid))

    def _close(self):
        self.system.save()
        self.destroy()
