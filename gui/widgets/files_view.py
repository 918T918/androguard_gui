from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class FilesView(QTreeWidget):
    fileSelected = pyqtSignal(str, bytes) # path, data

    def __init__(self, apk):
        super().__init__()
        self.apk = apk
        self.setHeaderLabel("APK Files")
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.populate()

    def populate(self):
        self.clear()
        self.item_cache = {"": self.invisibleRootItem()}
        
        # get_files() returns a list of filenames
        for filename in self.apk.get_files():
            parts = filename.split('/')
            parent_path = ""
            for i, part in enumerate(parts):
                path = "/".join(parts[:i+1])
                if path not in self.item_cache:
                    parent = self.item_cache[parent_path]
                    item = QTreeWidgetItem(parent, [part])
                    self.item_cache[path] = item
                parent_path = path
            
            # The last item is the file
            self.item_cache[filename].setData(0, Qt.ItemDataRole.UserRole, filename)

    def on_item_double_clicked(self, item, col):
        filename = item.data(0, Qt.ItemDataRole.UserRole)
        if filename:
            try:
                data = self.apk.get_file(filename)
                self.fileSelected.emit(filename, data)
            except Exception:
                pass
