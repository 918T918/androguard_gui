from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt

class ProjectTree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Project Structure")
        self.apk = None
        self.classes_dex = None
        self.analysis = None

    def populate(self, apk, classes_dex, analysis):
        self.clear()
        self.apk = apk
        self.classes_dex = classes_dex
        self.analysis = analysis

        manifest_item = QTreeWidgetItem(self, ["AndroidManifest.xml"])
        manifest_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'manifest', 'obj': apk})
        
        classes_root = QTreeWidgetItem(self, ["Classes"])
        
        
        for d in classes_dex:
            for current_class in d.get_classes():
                name = current_class.get_name()
                if not name: continue
                
                raw_name = name[1:-1]
                parts = raw_name.split('/')
                
                current_item = classes_root
                path_so_far = ""
                
                
                
                
                self.add_class_to_tree(classes_root, parts, current_class)

    def add_class_to_tree(self, parent_item, parts, class_obj):
        
        pass

    def populate(self, apk, classes_dex, analysis):
        self.clear()
        self.apk = apk
        
        manifest = QTreeWidgetItem(self, ["AndroidManifest.xml"])
        manifest.setData(0, Qt.ItemDataRole.UserRole, {'type': 'manifest', 'obj': apk})
        
        dex_root = QTreeWidgetItem(self, ["Classes"])
        
        self.item_cache = {"": dex_root}
        
        for d in classes_dex:
            for cls in d.get_classes():
                name = str(cls.get_name())
                clean_name = name[1:-1]
                
                parts = [str(p) for p in clean_name.split('/')]
                class_name = parts[-1]
                package_path = "/".join(parts[:-1])
                
                parent_item = self.get_or_create_package(dex_root, package_path)
                
                class_item = QTreeWidgetItem(parent_item, [class_name])
                class_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'class', 'obj': cls})

    def get_or_create_package(self, root, package_path):
        if package_path in self.item_cache:
            return self.item_cache[package_path]
        
        if package_path == "":
            return root
            
        parent_path, _, current_dir = package_path.rpartition('/')
        parent_item = self.get_or_create_package(root, parent_path)
        
        new_item = QTreeWidgetItem(parent_item, [current_dir])
        self.item_cache[package_path] = new_item
        return new_item
