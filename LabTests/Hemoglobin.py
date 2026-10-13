from .LabTest import LabTest

class Hemoglobin(LabTest):
    NAME, UNIT = "Hemoglobin", "g/dL"

    def reference_range(self, sex):
        return (13.5, 17.5) if sex == "Male" else (12.0, 15.5)

    def advice(self, status):
        return ("Low hemoglobin (anemia) is common in chronic kidney disease."
                if status == "Low" else "High hemoglobin should be reviewed by a doctor.")