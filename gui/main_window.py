from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QFileDialog, QToolBar, QStatusBar, QMessageBox, QDockWidget)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize

from core.analyzer import AnalysisThread
from gui.widgets.info_tab import InfoTab
from gui.widgets.tree_view import ProjectTree
from gui.widgets.code_editor import CodeEditorTab
from gui.widgets.strings_view import StringsView
from gui.widgets.device_dialog import DeviceDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Androguard GUI")
        self.resize(1200, 800)
        
        self.apk_path = None
        self.analysis_thread = None
        self.dx = None
        
        # UI Setup
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
    def setup_ui(self):
        # Central Widget - Tabs for different views (Code, Manifest, Strings, etc.)
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(True)
        self.central_tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.central_tabs)
        
        # Dock Widget - Project Tree
        self.tree_dock = QDockWidget("Project Structure", self)
        self.tree_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.project_tree = ProjectTree()
        self.project_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_dock.setWidget(self.project_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tree_dock)
        
        # Info Tab (Always present or first loaded)
        self.info_tab = InfoTab()
        self.central_tabs.addTab(self.info_tab, "Dashboard")
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open APK...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_apk_dialog)
        file_menu.addAction(open_action)
        
        # Device Menu
        device_menu = menubar.addMenu("&Device")
        list_packages_action = QAction("&List Packages...", self)
        list_packages_action.triggered.connect(self.open_device_dialog)
        device_menu.addAction(list_packages_action)
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        # Add toggles for docks later

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        open_action = QAction("Open APK", self)
        open_action.triggered.connect(self.open_apk_dialog)
        toolbar.addAction(open_action)
        
        device_action = QAction("List Packages", self)
        device_action.triggered.connect(self.open_device_dialog)
        toolbar.addAction(device_action)

    def open_apk_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open APK", "", "APK Files (*.apk);;All Files (*)")
        if file_name:
            self.load_apk(file_name)

    def open_device_dialog(self):
        dialog = DeviceDialog(self)
        if dialog.exec():
            if dialog.selected_apk_path:
                self.load_apk(dialog.selected_apk_path)

    def load_apk(self, path):
        self.apk_path = path
        self.status_bar.showMessage(f"Loading {path}...")
        self.project_tree.clear()
        
        # Start background analysis
        self.analysis_thread = AnalysisThread(path)
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.progress.connect(self.on_analysis_progress)
        self.analysis_thread.error.connect(self.on_analysis_error)
        self.analysis_thread.start()
        
        # Disable interactions that require loaded data
        self.project_tree.setEnabled(False)

    def on_analysis_progress(self, msg):
        self.status_bar.showMessage(msg)

    def on_analysis_finished(self, apk, classes, dex):
        self.status_bar.showMessage("Analysis Complete")
        self.dx = dex # Wait, the signature in analyzer.py was (a, d, dx).
        # In analyzer.py: self.finished.emit(a, d, dx)
        # So here it is (apk, classes_dex_list, analysis_obj)
        # But wait, my signature in on_analysis_finished is (apk, classes, dex). 
        # Variable naming is confusing. 
        # analyzer.py: finished.emit(a, d, dx) -> (APK, [DalvikVMFormat], Analysis)
        # So 'classes' is [DalvikVMFormat], 'dex' is Analysis.
        # Let's rename for clarity.
        
        self.dx = dex 
        self.project_tree.setEnabled(True)
        self.project_tree.populate(apk, classes, dex)
        self.info_tab.update_info(apk)
        
        # Add Strings Tab
        self.strings_view = StringsView(dex)
        self.strings_view.stringClicked.connect(self.open_method_from_string)
        self.central_tabs.addTab(self.strings_view, "Strings")
        
    def on_analysis_error(self, msg):
        self.status_bar.showMessage(f"Error: {msg}")
        QMessageBox.critical(self, "Error", f"Failed to analyze APK:\n{msg}")
        self.project_tree.setEnabled(True)

    def open_method_from_string(self, method_obj):
        self.open_code_tab(method_obj, is_method=True)

    def on_tree_item_clicked(self, item, column):
        # Handle opening classes/methods from tree
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
            
        # Example: data = {'type': 'class', 'obj': class_obj}
        if data['type'] == 'class':
            self.open_code_tab(data['obj'], is_method=False)
        elif data['type'] == 'method':
            self.open_code_tab(data['obj'], is_method=True)

    def open_code_tab(self, obj, is_method=False):
        # Check if already open
        name = obj.get_name() if hasattr(obj, 'get_name') else str(obj)
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        
        editor = CodeEditorTab(obj, is_method, dx=self.dx)
        self.central_tabs.addTab(editor, name)
        self.central_tabs.setCurrentWidget(editor)

    def close_tab(self, index):
        self.central_tabs.removeTab(index)
