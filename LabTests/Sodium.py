from .LabTest import LabTest

class Sodium(LabTest):
    NAME, UNIT = "Sodium", "mmol/L"

    def reference_range(self, sex):
        return (135, 145)

    def advice(self, status):
        return "Sodium out of range relates to fluid balance; a doctor should review it."