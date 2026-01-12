from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QListWidget, 
                             QPushButton, QLabel, QProgressBar, QHBoxLayout, QMessageBox, QListWidgetItem,
                             QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from androguard.decompiler.dad.decompile import DvClass

class SearchThread(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    
    def __init__(self, dx, query):
        super().__init__()
        self.dx = dx
        self.query = query.lower()
        
    def run(self):
        results = []
        classes = list(self.dx.get_classes())
        total = len(classes)
        
        for i, c in enumerate(classes):
            if i % 100 == 0:
                self.progress.emit(int((i / total) * 100))
            if self.query in c.name.lower():
                results.append(('class', c.get_vm_class()))
            for m in c.get_methods():
                if self.query in m.name.lower():
                    results.append(('method', m.get_method()))
        self.finished.emit(results)

class FullTextSearchThread(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int, str) # progress, current_class
    
    def __init__(self, dx, query):
        super().__init__()
        self.dx = dx
        self.query = query.lower()
        
    def run(self):
        results = []
        classes = list(self.dx.get_classes())
        total = len(classes)
        
        for i, c_analysis in enumerate(classes):
            if i % 10 == 0:
                self.progress.emit(int((i / total) * 100), c_analysis.name)
            
            try:
                cls = c_analysis.get_vm_class()
                dv = DvClass(cls, self.dx)
                dv.process()
                source = dv.get_source().lower()
                
                if self.query in source:
                    results.append(('class', cls))
            except Exception:
                continue
                
        self.finished.emit(results)

class SearchDialog(QDialog):
    def __init__(self, parent, dx):
        super().__init__(parent)
        self.setWindowTitle("Search Symbols & Code")
        self.resize(600, 600)
        self.dx = dx
        self.selected_obj = None
        self.selected_type = None
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        h_layout = QHBoxLayout()
        self.search_mode = QComboBox()
        self.search_mode.addItems(["Symbol Names (Fast)", "Full-Text Code (Slow)"])
        h_layout.addWidget(QLabel("Mode:"))
        h_layout.addWidget(self.search_mode, 1)
        layout.addLayout(h_layout)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search query...")
        self.query_input.returnPressed.connect(self.start_search)
        layout.addWidget(self.query_input)
        
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.start_search)
        layout.addWidget(btn_search)
        
        self.progress_label = QLabel("")
        self.progress_label.hide()
        layout.addWidget(self.progress_label)
        
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.results_list)
        
        self.setLayout(layout)

    def start_search(self):
        query = self.query_input.text().strip()
        if not query: return
        
        self.results_list.clear()
        self.progress.setValue(0)
        self.progress.show()
        
        if self.search_mode.currentIndex() == 0:
            self.progress_label.hide()
            self.thread = SearchThread(self.dx, query)
            self.thread.progress.connect(self.progress.setValue)
        else:
            self.progress_label.show()
            self.thread = FullTextSearchThread(self.dx, query)
            self.thread.progress.connect(self.on_fulltext_progress)
            
        self.thread.finished.connect(self.on_search_finished)
        self.thread.start()

    def on_fulltext_progress(self, val, cls_name):
        self.progress.setValue(val)
        self.progress_label.setText(f"Searching: {cls_name}")

    def on_search_finished(self, results):
        self.progress.hide()
        self.progress_label.hide()
        if not results:
            QMessageBox.information(self, "Search", "No results found.")
            return
            
        for type_, obj in results:
            name = obj.get_name()
            item = QListWidgetItem(f"[{type_}] {name}")
            item.setData(Qt.ItemDataRole.UserRole, (type_, obj))
            self.results_list.addItem(item)

    def on_item_double_clicked(self, item):
        type_, obj = item.data(Qt.ItemDataRole.UserRole)
        self.selected_type = type_
        self.selected_obj = obj
        self.accept()