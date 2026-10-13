from .LabTest import LabTest


class Creatinine(LabTest):
    NAME, UNIT = "Creatinine", "mg/dL"

    def reference_range(self, sex):
        return (0.7, 1.3) if sex == "Male" else (0.6, 1.1)

    def advice(self, status):
        return ("High creatinine can mean the kidneys are filtering less well."
                if status == "High" else "Low creatinine is usually related to low muscle mass.")