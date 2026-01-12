from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class StringsView(QWidget):
    stringClicked = pyqtSignal(object) # signal emitting (class_obj, method_obj) or similar

    def __init__(self, analysis):
        super().__init__()
        self.analysis = analysis
        self.setup_ui()
        self.populate()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Filter
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search strings...")
        self.filter_input.textChanged.connect(self.filter_strings)
        layout.addWidget(self.filter_input)
        
        # Table
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
            
        # This can be huge. We should probably limit or lazy load.
        # For prototype, lets take first 1000 or so, or all if reasonable.
        # Strings can be 50k+.
        # We'll just load them all for now, but in a thread if possible?
        # Let's just load them.
        
        # self.all_strings = list(self.analysis.get_strings())
        # Actually androguard 3.4 'get_strings()' returns StringAnalysis objects? 
        # No, 'dx.get_strings()' returns list of StringAnalysis.
        # string_analysis.get_value()
        
        self.strings = []
        for s in self.analysis.get_strings():
            self.strings.append(s)
            
        self.update_table(self.strings)

    def update_table(self, strings_list):
        self.table.setRowCount(0)
        # Limit display for performance
        limit = 1000
        self.table.setRowCount(min(len(strings_list), limit))
        
        for i, s in enumerate(strings_list[:limit]):
            val = s.get_value()
            item = QTableWidgetItem(val)
            item.setData(Qt.ItemDataRole.UserRole, s)
            self.table.setItem(i, 0, item)

    def filter_strings(self, text):
        filtered = [s for s in self.strings if text.lower() in s.get_value().lower()]
        self.update_table(filtered)

    def on_cell_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        s_obj = item.data(Qt.ItemDataRole.UserRole)
        
        # Find XREFs
        # In a real app, show a dialog with XREFs. 
        # For now, just print or try to open the first one.
        xrefs = s_obj.get_xref_from()
        
        # xrefs is a set of (ClassAnalysis, MethodAnalysis, offset)
        if xrefs:
            # Pick first
            class_analysis, method_analysis, offset = next(iter(xrefs))
            # method_analysis is MethodAnalysis.
            # We want to open this method.
            # method_analysis.get_method() returns EncodedMethod (raw).
            
            # Signal: open this method
            self.stringClicked.emit(method_analysis.get_method())
