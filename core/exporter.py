from PyQt6.QtCore import QThread, pyqtSignal
from androguard.decompiler.dad.decompile import DvClass
import os

class ExportThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, dx, out_dir):
        super().__init__()
        self.dx = dx
        self.out_dir = out_dir

    def run(self):
        classes = list(self.dx.get_classes())
        for c_analysis in classes:
            try:
                cls = c_analysis.get_vm_class()
                name = cls.get_name()[1:-1] # a/b/c
                self.progress.emit(name)
                
                # Create directory structure
                parts = name.split('/')
                package_dir = os.path.join(self.out_dir, *parts[:-1])
                os.makedirs(package_dir, exist_ok=True)
                
                # Decompile
                dv = DvClass(cls, self.dx)
                dv.process()
                
                # Save
                file_path = os.path.join(self.out_dir, name + ".java")
                with open(file_path, "w") as f:
                    f.write(dv.get_source())
            except Exception as e:
                print(f"Error exporting {name}: {e}")
                
        self.finished.emit()
