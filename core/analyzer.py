from PyQt6.QtCore import QThread, pyqtSignal
from androguard.misc import AnalyzeAPK
import traceback

class AnalysisThread(QThread):
    finished = pyqtSignal(object, object, object) # apk, classes, dex
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, apk_path):
        super().__init__()
        self.apk_path = apk_path

    def run(self):
        try:
            self.progress.emit(f"Analyzing {self.apk_path}...")
            # AnalyzeAPK returns: a, d, dx
            # a: APK object
            # d: list of DalvikVMFormat objects (one per dex)
            # dx: Analysis object
            a, d, dx = AnalyzeAPK(self.apk_path)
            
            self.progress.emit("Analysis finished. building UI...")
            self.finished.emit(a, d, dx)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))
