from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
                             QLabel, QPushButton, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class ScannerThread(QThread):
    found = pyqtSignal(str, object, str)
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    HOTSPOTS = {
        "Crypto": ["Ljavax/crypto/Cipher;", "Ljava/security/MessageDigest;"],
        "Network": ["Ljava/net/URL;", "Lokhttp3/OkHttpClient;", "Lorg/apache/http/client/HttpClient;"],
        "Reflection": ["Ljava/lang/reflect/Method;", "Ljava/lang/Class;->forName"],
        "Execution": ["Ljava/lang/Runtime;->exec", "Ljava/lang/ProcessBuilder;"],
        "Webview": ["Landroid/webkit/WebView;->loadUrl", "Landroid/webkit/WebView;->addJavascriptInterface"],
        "File": ["Ljava/io/File;"],
        "SMS": ["Landroid/telephony/SmsManager;"]
    }

    def __init__(self, dx):
        super().__init__()
        self.dx = dx

    def run(self):
        classes = list(self.dx.get_classes())
        total = len(classes)
        
        for i, c in enumerate(classes):
            if i % 50 == 0:
                self.progress.emit(int((i / total) * 100))
                
            for method in c.get_methods():
                m_obj = method.get_method()
                code = m_obj.get_code()
                if not code: continue
                
                for ins in code.get_instructions():
                    output = ins.get_output()
                    for category, keywords in self.HOTSPOTS.items():
                        for k in keywords:
                            if k in output:
                                desc = f"{category} call: {output}"
                                self.found.emit(category, m_obj, desc)
        self.finished.emit()

class ScannerTab(QWidget):
    methodSelected = pyqtSignal(object)

    def __init__(self, dx):
        super().__init__()
        self.dx = dx
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.btn_scan = QPushButton("Start Security Scan")
        self.btn_scan.clicked.connect(self.start_scan)
        layout.addWidget(self.btn_scan)
        
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        self.results = QListWidget()
        self.results.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.results)
        
        self.setLayout(layout)

    def start_scan(self):
        self.results.clear()
        self.btn_scan.setEnabled(False)
        self.progress.show()
        
        self.thread = ScannerThread(self.dx)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.found.connect(self.on_found)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_found(self, category, method, desc):
        item = QListWidgetItem(f"[{category}] {method.get_class_name()}->{method.get_name()}")
        item.setToolTip(desc)
        item.setData(Qt.ItemDataRole.UserRole, method)
        self.results.addItem(item)

    def on_finished(self):
        self.btn_scan.setEnabled(True)
        self.progress.hide()
        QMessageBox.information(self, "Scan Complete", f"Found {self.results.count()} hotspots.")

    def on_item_double_clicked(self, item):
        self.methodSelected.emit(item.data(Qt.ItemDataRole.UserRole))
