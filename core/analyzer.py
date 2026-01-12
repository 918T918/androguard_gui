from PyQt6.QtCore import QThread, pyqtSignal
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
from androguard.core.analysis.analysis import Analysis
import traceback

class AnalysisThread(QThread):
    finished = pyqtSignal(object, object, object) # apk, classes, dex
    progress = pyqtSignal(str, int) # message, percentage
    error = pyqtSignal(str)

    def __init__(self, apk_path):
        super().__init__()
        self.apk_path = apk_path

    def run(self):
        try:
            self.progress.emit(f"Loading APK: {self.apk_path}...", 10)
            a = APK(self.apk_path)
            
            self.progress.emit("Parsing DEX files...", 30)
            dex_files = []
            all_dex = list(a.get_all_dex())
            total_dex = len(all_dex)
            
            for i, dex_data in enumerate(all_dex):
                self.progress.emit(f"Parsing DEX {i+1}/{total_dex}...", 30 + int((i/total_dex) * 20))
                dex_files.append(DalvikVMFormat(dex_data))
            
            self.progress.emit("Initializing Analysis engine...", 60)
            dx = Analysis()
            for i, d in enumerate(dex_files):
                self.progress.emit(f"Adding DEX {i+1} to Analysis...", 60 + int((i/total_dex) * 10))
                dx.add(d)
            
            self.progress.emit("Creating Cross-References (XREFs)...", 80)
            dx.create_xref()
            
            self.progress.emit("Analysis finished. building UI...", 100)
            self.finished.emit(a, dex_files, dx)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))