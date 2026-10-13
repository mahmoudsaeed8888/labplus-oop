from .LabTest import LabTest

class Urea(LabTest):
    NAME, UNIT = "Urea", "mg/dL"

    def reference_range(self, sex):
        return (7, 20)

    def advice(self, status):
        return ("High urea can be linked to reduced kidney function or dehydration."
                if status == "High" else "Low urea can relate to low protein intake or liver issues.")