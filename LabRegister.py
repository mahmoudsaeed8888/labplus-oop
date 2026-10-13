from LabTests import Creatinine, Urea, Potassium, Sodium, Hemoglobin, Albumin

TEST_TYPES = {c.NAME: c for c in (Creatinine, Urea, Potassium, Sodium, Hemoglobin, Albumin)}
ALIASES = {n.lower(): n for n in TEST_TYPES}
ALIASES.update({"cr": "Creatinine", "serum creatinine": "Creatinine", "scr": "Creatinine",
                "bun": "Urea", "blood urea": "Urea", "k": "Potassium", "k+": "Potassium",
                "na": "Sodium", "na+": "Sodium", "hb": "Hemoglobin", "hgb": "Hemoglobin",
                "alb": "Albumin"})

def normalize_name(text):
    """Name normalization: Cr = Serum Creatinine = Creatinine, etc."""
    key = str(text).strip().lower()
    if key not in ALIASES:
        raise ValueError(f"Unknown test '{text}'. Known: {', '.join(TEST_TYPES)}")
    return ALIASES[key]

def make_test(name, value, test_date, test_id=None):
    return TEST_TYPES[normalize_name(name)](value, test_date, test_id)
