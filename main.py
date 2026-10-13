from LabPlusSystem import LabPlusSystem
from LabPlusApp import LabPlusApp

if __name__ == "__main__":
    system = LabPlusSystem()
    system.load()
    LabPlusApp(system).mainloop()