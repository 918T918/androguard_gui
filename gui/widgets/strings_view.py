from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class StringsView(QWidget):
    stringClicked = pyqtSignal(object)

    def __init__(self, analysis):
        super().__init__()
        self.analysis = analysis
        self.setup_ui()
        self.populate()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search strings...")
        self.filter_input.textChanged.connect(self.filter_strings)
        layout.addWidget(self.filter_input)
        
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["String"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def populate(self):
        if not self.analysis:
            return
            
        
        
        self.strings = []
        for s in self.analysis.get_strings():
            self.strings.append(s)
            
        self.update_table(self.strings)

    def update_table(self, strings_list):
        self.table.setRowCount(0)
        limit = 1000
        self.table.setRowCount(min(len(strings_list), limit))
        
        for i, s in enumerate(strings_list[:limit]):
            val = str(s.get_value())
            item = QTableWidgetItem(val)
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.table.setItem(i, 0, item)

    def filter_strings(self, text):
        filtered = [s for s in self.strings if text.lower() in str(s.get_value()).lower()]
        self.update_table(filtered)

    def on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        s_obj = item.data(Qt.ItemDataRole.UserRole)
        
        xrefs = s_obj.get_xref_from()
        
        if xrefs:
            class_analysis, method_analysis, offset = next(iter(xrefs))
            
            self.stringClicked.emit(method_analysis.get_method())
