from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
                             QLineEdit, QListWidget, QPushButton, QLabel, QMessageBox, 
                             QProgressDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.adb_manager import ADBManager
import os
import tempfile

class PullThread(QThread):
    finished = pyqtSignal(str) # returns path of pulled apk
    error = pyqtSignal(str)

    def __init__(self, adb, serial, remote_path, package_name):
        super().__init__()
        self.adb = adb
        self.serial = serial
        self.remote_path = remote_path
        self.package_name = package_name

    def run(self):
        try:
            # Create a temp file
            # We want to keep it valid for the session
            tmp_dir = os.path.join(tempfile.gettempdir(), "androguard_gui_pulls")
            os.makedirs(tmp_dir, exist_ok=True)
            local_filename = f"{self.package_name}.apk"
            local_path = os.path.join(tmp_dir, local_filename)
            
            self.adb.pull_apk(self.serial, self.remote_path, local_path)
            self.finished.emit(local_path)
        except Exception as e:
            self.error.emit(str(e))

class DeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Packages")
        self.resize(600, 500)
        
        self.adb = ADBManager()
        self.selected_apk_path = None # Result
        
        self.setup_ui()
        self.refresh_devices()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Top bar: Device Selector + Refresh
        top_layout = QHBoxLayout()
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.load_packages)
        top_layout.addWidget(QLabel("Device:"))
        top_layout.addWidget(self.device_combo, 1)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_devices)
        top_layout.addWidget(refresh_btn)
        
        layout.addLayout(top_layout)
        
        # Filter
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search packages...")
        self.filter_input.textChanged.connect(self.filter_packages)
        layout.addWidget(self.filter_input)
        
        # Package List
        self.package_list = QListWidget()
        layout.addWidget(self.package_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        self.pull_btn = QPushButton("Pull & Analyze")
        self.pull_btn.clicked.connect(self.pull_selected)
        self.pull_btn.setEnabled(False)
        self.package_list.itemSelectionChanged.connect(self.check_selection)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.pull_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def refresh_devices(self):
        self.device_combo.clear()
        try:
            devices = self.adb.get_devices()
            if devices:
                self.device_combo.addItems(devices)
            else:
                self.device_combo.addItem("No devices found")
                self.device_combo.setEnabled(False)
        except Exception as e:
            QMessageBox.warning(self, "ADB Error", str(e))

    def load_packages(self):
        if self.device_combo.count() == 0 or self.device_combo.itemText(0) == "No devices found":
            self.package_list.clear()
            return

        serial = self.device_combo.currentText()
        self.package_list.clear()
        self.packages = [] # Store (name, path)
        
        try:
            # Show simple loading... (or use thread if slow)
            self.packages = self.adb.get_packages(serial)
            self.update_list(self.packages)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_list(self, packages):
        self.package_list.clear()
        for name, path in packages:
            self.package_list.addItem(f"{name}  [{path}]")

    def filter_packages(self, text):
        if not hasattr(self, 'packages'): return
        
        filtered = [p for p in self.packages if text.lower() in p[0].lower()]
        self.update_list(filtered)

    def check_selection(self):
        self.pull_btn.setEnabled(len(self.package_list.selectedItems()) > 0)

    def pull_selected(self):
        item = self.package_list.selectedItems()[0]
        # Parse text to get name/path again or lookup
        # Format: "{name}  [{path}]"
        text = item.text()
        name = text.split("  [")[0]
        
        # Find path in self.packages
        path = None
        for p_name, p_path in self.packages:
            if p_name == name:
                path = p_path
                break
        
        if not path:
            return

        serial = self.device_combo.currentText()
        
        # Start Pull Thread
        self.progress = QProgressDialog("Pulling APK...", "Cancel", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        
        self.thread = PullThread(self.adb, serial, path, name)
        self.thread.finished.connect(self.on_pull_finished)
        self.thread.error.connect(self.on_pull_error)
        self.thread.start()

    def on_pull_finished(self, local_path):
        self.progress.cancel()
        self.selected_apk_path = local_path
        self.accept()

    def on_pull_error(self, msg):
        self.progress.cancel()
        QMessageBox.critical(self, "Pull Error", msg)
