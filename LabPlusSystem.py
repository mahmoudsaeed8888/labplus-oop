import json 
from patient import Patient 
from LabRegister import TEST_TYPES, make_test

DATA_FILE = "labplus_data.json"
class LabPlusSystem:
    def __init__(self):
        self.__patients = {}

    # ids: always (highest existing id + 1), so they restart from 1 when the
    # list is empty and are never "burned" by failed/invalid input
    def _next_patient_id(self):
        return max(self.__patients, default=0) + 1

    def _next_result_id(self):
        return max((r.id for p in self.__patients.values() for r in p.results), default=0) + 1

    # patients
    def add_patient(self, name, age, sex):
        p = Patient(name, age, sex, patient_id=self._next_patient_id())
        self.__patients[p.id] = p
        return p

    def get_patient(self, pid):
        return self.__patients[pid]

    def update_patient(self, pid, name, age, sex):
        Patient(name, age, sex, patient_id=pid)  # validate first
        p = self.__patients[pid]
        p.name, p.age, p.sex = name, age, sex

    def delete_patient(self, pid):
        del self.__patients[pid]

    def search_patients(self, text=""):
        t = text.lower().strip()
        return [p for p in self.__patients.values() if not t or t in p.name.lower()]

    # results
    def add_result(self, pid, name, value, test_date):
        self.get_patient(pid).add_result(make_test(name, value, test_date, self._next_result_id()))

    def update_result(self, pid, test_id, name, value, test_date):
        self.get_patient(pid).replace_result(test_id, make_test(name, value, test_date, test_id))

    def delete_result(self, pid, test_id):
        self.get_patient(pid).remove_result(test_id)

    def search_results(self, pid, text=""):
        t = text.lower().strip()
        rs = [r for r in self.get_patient(pid).results
              if not t or t in r.name.lower() or t in r.date]
        return sorted(rs, key=lambda r: (r.date, r.id), reverse=True)

    def explain(self, pid):
        """Chatbot-style summary of the latest result per test + trend."""
        p = self.get_patient(pid)
        if not p.results:
            return "No results yet for this patient."
        out = [f"Summary for {p.name}:\n"]
        for name in TEST_TYPES:
            rs = sorted([r for r in p.results if r.name == name], key=lambda r: (r.date, r.id))
            if not rs:
                continue
            cur = rs[-1]
            lo, hi = cur.reference_range(p.sex)
            st = cur.status(p.sex)
            line = f"- {name}: {cur.value:g} {cur.unit} ({st}, normal {lo:g}-{hi:g})"
            out.append(line)
            if st != "Normal":
                out.append(f"    {cur.advice(st)}")
            if len(rs) > 1:
                d_new, d_old = cur.deviation(p.sex), rs[-2].deviation(p.sex)
                if d_new == d_old == 0:
                    trend = "stable within the normal range"
                elif d_new < d_old:
                    trend = "improved compared with the previous test"
                elif d_new > d_old:
                    trend = "worse compared with the previous test"
                else:
                    trend = "unchanged"
                out.append(f"    Trend: {trend} (previous {rs[-2].value:g} on {rs[-2].date})")
        out.append("\nThis is NOT a medical diagnosis. Please consult your doctor.")
        return "\n".join(out)

    # persistence
    def save(self, path=DATA_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in self.__patients.values()], f, indent=2)

    def load(self, path=DATA_FILE):
        try:
            with open(path, encoding="utf-8") as f:
                for d in json.load(f):
                    p = Patient(d["name"], d["age"], d["sex"], patient_id=d["id"])
                    for r in d["results"]:
                        p.add_result(make_test(r["name"], r["value"], r["date"], r["id"]))
                    self.__patients[p.id] = p
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            pass
