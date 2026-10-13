class Patient:
    next_id = 1

    def __init__(self, name, age, sex, patient_id=None):
        if patient_id is None:
            patient_id = Patient.next_id
        Patient.next_id = max(Patient.next_id, patient_id + 1)
        self._id = patient_id
        self.name = name
        self.age = age
        self.sex = sex
        self.__results = []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        v = str(v).strip()
        if not v:
            raise ValueError("Patient name cannot be empty.")
        self._name = v

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, v):
        try:
            v = int(v)
        except (TypeError, ValueError):
            raise ValueError("Age must be a number.")
        if not 0 < v < 130:
            raise ValueError("Age must be between 1 and 129.")
        self._age = v

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, v):
        if v not in ("Male", "Female"):
            raise ValueError("Sex must be Male or Female.")
        self._sex = v

    @property
    def results(self):
        return list(self.__results)

    def add_result(self, test):
        self.__results.append(test)

    def replace_result(self, test_id, new_test):
        for i, t in enumerate(self.__results):
            if t.id == test_id:
                self.__results[i] = new_test
                return
        raise KeyError(test_id)

    def remove_result(self, test_id):
        self.__results = [t for t in self.__results if t.id != test_id]

    def to_dict(self):
        return {"id": self._id, "name": self._name, "age": self._age, "sex": self._sex,
                "results": [t.to_dict() for t in self.__results]}