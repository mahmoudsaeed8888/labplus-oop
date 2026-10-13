# LabPlus (OOP Project)

Object-oriented implementation of **LabPlus**, a kidney lab report analysis system, built with Python and Tkinter.

The app lets you manage patients and their kidney-related lab results, then generates a simple chatbot-style summary that flags abnormal values and shows the trend compared with the previous test.

> **Disclaimer:** This is a preliminary analysis only, not a medical diagnosis. Always consult a doctor.

## Features

- Add, update, delete, and search patients
- Add, update, delete, and search lab results for each patient
- Supported tests: Creatinine, Urea, Potassium, Sodium, Hemoglobin, Albumin
- Automatic status (Low / Normal / High) based on the patient's sex
- Plain-language advice for abnormal results
- Trend detection (improved / worse / stable) vs. the previous test
- Name normalization (e.g. `Cr` = `Serum Creatinine` = `Creatinine`)
- Data saved to a local JSON file
- Desktop GUI built with Tkinter

## OOP Concepts Used

| Concept | Where |
|---|---|
| **Abstraction** | `LabTest` is an abstract base class (`ABC`) with abstract methods `reference_range()` and `advice()` |
| **Inheritance** | `Creatinine`, `Urea`, `Potassium`, `Sodium`, `Hemoglobin`, `Albumin` inherit from `LabTest` |
| **Polymorphism** | Each test type gives its own reference range and advice, while the system treats them all as `LabTest` |
| **Encapsulation** | Private attributes, properties with validation (`Patient.age`, `LabTest.value`, `LabTest.date`), and private patient storage in `LabPlusSystem` |
| **Composition** | A `Patient` has many lab results; `LabPlusSystem` manages many patients; `LabPlusApp` uses a `LabPlusSystem` |
| **Factory function** | `make_test()` in `LabRegister.py` creates the right test class from a name |

## Project Structure

```
LaBPlus_project/
├── main.py              # Entry point
├── LabPlusApp.py        # Tkinter GUI
├── LabPlusSystem.py     # Core logic: patients, results, explanation, save/load
├── patient.py           # Patient class
├── LabRegister.py       # Test registry, name normalization, make_test()
└── LabTests/
    ├── LabTest.py       # Abstract base class
    ├── Creatinine.py
    ├── Urea.py
    ├── Potassium.py
    ├── Sodium.py
    ├── Hemoglobin.py
    └── Albumin.py
```

## How to Run

Requirements: **Python 3.8+** (Tkinter comes bundled with the standard Python installer on Windows).

```bash
git clone https://github.com/USERNAME/REPO-NAME.git
cd REPO-NAME
python main.py
```

## Author

Mahmoud Saeed El-Azab
