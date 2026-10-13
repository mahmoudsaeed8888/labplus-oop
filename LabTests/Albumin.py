from .LabTest import LabTest

class Albumin(LabTest):
    NAME, UNIT = "Albumin", "g/dL"

    def reference_range(self, sex):
        return (3.5, 5.0)

    def advice(self, status):
        return "Low albumin can be a sign of protein loss or poor nutrition." if status == "Low" \
            else "High albumin is often due to dehydration."