import json
from abc import ABC, abstractmethod
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "labplus_data.json"


# ------------------------------ Lab tests ------------------------------
class LabTest(ABC):
    next_id = 1
    NAME = ""
    UNIT = ""

    def __init__(self, value, test_date, test_id=None):
        if test_id is None:
            test_id = LabTest.next_id
        LabTest.next_id = max(LabTest.next_id, test_id + 1)
        self._id = test_id
        self.value = value
        self.date = test_date

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self.NAME

    @property
    def unit(self):
        return self.UNIT

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        try:
            v = float(v)
        except ValueError :
            raise ValueError("Value must be a number ")
        if v < 0:
            raise ValueError("Value cannot be negative ")
        self._value = v

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, v):
        v = str(v).strip()
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format ")
        self._date = v

    @abstractmethod
    def reference_range(self, sex):
        " Return (low, high) normal range "

    @abstractmethod
    def advice(self, status):
        " Simple explanation  "

    def status(self, sex):
        lo, hi = self.reference_range(sex)
        return "Low" if self._value < lo else "High" if self._value > hi else "Normal"

    def deviation(self, sex): # بنقيس القيمه اللي طلعت بعيده قد ايه عن النورمال 
        "Relative distance outside the normal range "
        lo, hi = self.reference_range(sex)
        if self._value < lo:
            return (lo - self._value) / lo
        if self._value > hi:
            return (self._value - hi) / hi
        return 0.0

    def to_dict(self):
        return {"name": self.NAME, "value": self._value, "date": self._date, "id": self._id}

    
