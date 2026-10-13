from .LabTest import LabTest

class Potassium(LabTest):
    NAME, UNIT = "Potassium", "mmol/L"

    def reference_range(self, sex):
        return (3.5, 5.0)

    def advice(self, status):
        return ("High potassium is important to follow up quickly with a doctor."
                if status == "High" else "Low potassium can cause weakness and cramps.")
