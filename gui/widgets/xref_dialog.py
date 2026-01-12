from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from PyQt6.QtCore import Qt

class XRefDialog(QDialog):
    def __init__(self, parent, xrefs, title="Cross References"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(600, 400)
        self.xrefs = xrefs
        self.selected_method = None
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        lbl = QLabel(f"Found {len(self.xrefs)} references:")
        layout.addWidget(lbl)
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        for class_analysis, method_analysis, offset in self.xrefs:
            method_name = method_analysis.get_method().get_name()
            class_name = class_analysis.get_name()
            
            text = f"{class_name} -> {method_name} (offset: {offset})"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, method_analysis.get_method())
            self.list_widget.addItem(item)
            
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def on_item_double_clicked(self, item):
        self.selected_method = item.data(Qt.ItemDataRole.UserRole)
        self.accept()
