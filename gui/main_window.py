from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QFileDialog, QToolBar, QStatusBar, QMessageBox, QDockWidget, QMenu)
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QSize, QSettings
import os

from core.analyzer import AnalysisThread
from gui.widgets.info_tab import InfoTab
from gui.widgets.tree_view import ProjectTree
from gui.widgets.code_editor import CodeEditorTab
from gui.widgets.strings_view import StringsView
from gui.widgets.device_dialog import DeviceDialog
from gui.widgets.manifest_viewer import ManifestViewer
from gui.widgets.xref_dialog import XRefDialog
from gui.widgets.cfg_window import CFGWindow
from gui.widgets.search_dialog import SearchDialog
from gui.widgets.cert_viewer import CertViewer
from gui.widgets.files_view import FilesView
from gui.widgets.hex_viewer import HexViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Androguard GUI")
        self.resize(1200, 800)
        
        self.settings = QSettings("Gemini", "AndroguardGUI")
        self.apk_path = None
        self.analysis_thread = None
        self.dx = None
        
        # Navigation History
        self.history = []
        self.history_index = -1
        self.navigating = False
        
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
        
        # Context Menu for Tree
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.open_tree_context_menu)
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
        self.file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open APK...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_apk_dialog)
        self.file_menu.addAction(open_action)
        
        self.recent_menu = self.file_menu.addMenu("Recent Files")
        self.update_recent_files_menu()
        
        export_action = QAction("Export to Java...", self)
        export_action.triggered.connect(self.export_to_java)
        self.file_menu.addAction(export_action)
        
        self.file_menu.addSeparator()
        
        # Device Menu
        device_menu = menubar.addMenu("&Device")
        list_packages_action = QAction("&List Packages...", self)
        list_packages_action.triggered.connect(self.open_device_dialog)
        device_menu.addAction(list_packages_action)
        
        # Search Menu
        search_menu = menubar.addMenu("&Search")
        search_action = QAction("&Search Symbols...", self)
        search_action.setShortcut("Ctrl+Shift+F")
        search_action.triggered.connect(self.open_search_dialog)
        search_menu.addAction(search_action)
        
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
        
        toolbar.addSeparator()
        
        self.back_action = QAction("Back", self)
        self.back_action.setShortcut(QKeySequence.StandardKey.Back)
        self.back_action.triggered.connect(self.go_back)
        self.back_action.setEnabled(False)
        toolbar.addAction(self.back_action)
        
        self.fwd_action = QAction("Forward", self)
        self.fwd_action.setShortcut(QKeySequence.StandardKey.Forward)
        self.fwd_action.triggered.connect(self.go_forward)
        self.fwd_action.setEnabled(False)
        toolbar.addAction(self.fwd_action)

    def open_apk_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open APK", "", "APK Files (*.apk);;All Files (*)")
        if file_name:
            self.load_apk(file_name)

    def open_device_dialog(self):
        dialog = DeviceDialog(self)
        if dialog.exec():
            if dialog.selected_apk_path:
                self.load_apk(dialog.selected_apk_path)

    def open_search_dialog(self):
        if not self.dx:
            QMessageBox.warning(self, "Search", "Please load and analyze an APK first.")
            return
        dialog = SearchDialog(self, self.dx)
        if dialog.exec():
            if dialog.selected_obj:
                is_method = (dialog.selected_type == 'method')
                self.open_code_tab(dialog.selected_obj, is_method=is_method)

    def load_apk(self, path):
        self.apk_path = path
        self.add_to_recent_files(path)
        self.status_bar.showMessage(f"Loading {path}...")
        self.project_tree.clear()
        
        # Reset History
        self.history = []
        self.history_index = -1
        self.update_nav_buttons()
        
        # Close all tabs except info
        while self.central_tabs.count() > 1:
            self.central_tabs.removeTab(1)
        
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
        
        # Add Manifest Tab
        self.manifest_view = ManifestViewer(apk)
        self.central_tabs.insertTab(1, self.manifest_view, "Manifest")
        
        # Add Files Tab
        self.files_view = FilesView(apk)
        self.files_view.fileSelected.connect(self.open_hex_tab)
        self.central_tabs.addTab(self.files_view, "Files")
        
        # Add Certificates Tab
        self.cert_view = CertViewer(apk)
        self.central_tabs.addTab(self.cert_view, "Certificates")
        
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

    def open_hex_tab(self, path, data):
        # Check if already open
        name = f"Hex: {os.path.basename(path)}"
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        
        viewer = HexViewer(data)
        self.central_tabs.addTab(viewer, name)
        self.central_tabs.setCurrentWidget(viewer)

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
            
    def open_tree_context_menu(self, position):
        item = self.project_tree.itemAt(position)
        if not item: return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data: return
        
        menu = QMenu()
        
        if data['type'] == 'method':
            method_obj = data['obj']
            action_xref = menu.addAction("Find Usages (XRefs)")
            action_cfg = menu.addAction("View Control Flow Graph")
            
            action = menu.exec(self.project_tree.viewport().mapToGlobal(position))
            
            if action == action_xref:
                self.show_xrefs(method_obj)
            elif action == action_cfg:
                self.show_cfg(method_obj)
                
    def show_xrefs(self, method_obj):
        if not self.dx: return
        
        # get_method return MethodAnalysis
        ma = self.dx.get_method(method_obj)
        if not ma:
            QMessageBox.information(self, "XRefs", "No analysis data for this method.")
            return
            
        # get_xref_from returns (ClassAnalysis, MethodAnalysis, offset)
        xrefs = list(ma.get_xref_from())
        
        if not xrefs:
            QMessageBox.information(self, "XRefs", "No references found.")
            return
            
        dialog = XRefDialog(self, xrefs)
        if dialog.exec():
            # Go to selected method
            self.open_code_tab(dialog.selected_method, is_method=True)

    def show_cfg(self, method_obj):
        if not self.dx: return
        self.cfg_window = CFGWindow(method_obj, self.dx)
        self.cfg_window.show()

    def open_code_tab(self, obj, is_method=False):
        # Record history if not navigating back/fwd
        if not self.navigating:
            self.add_history(obj, is_method)

        name = obj.get_name() if hasattr(obj, 'get_name') else str(obj)
        
        # Check if already open
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        
        editor = CodeEditorTab(obj, is_method, dx=self.dx)
        self.central_tabs.addTab(editor, name)
        self.central_tabs.setCurrentWidget(editor)

    def close_tab(self, index):
        self.central_tabs.removeTab(index)
        
    def add_history(self, obj, is_method):
        # Remove forward history
        self.history = self.history[:self.history_index+1]
        self.history.append((obj, is_method))
        self.history_index += 1
        self.update_nav_buttons()
        
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigating = True
            obj, is_method = self.history[self.history_index]
            self.open_code_tab(obj, is_method)
            self.navigating = False
            self.update_nav_buttons()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigating = True
            obj, is_method = self.history[self.history_index]
            self.open_code_tab(obj, is_method)
            self.navigating = False
            self.update_nav_buttons()
            
    def update_nav_buttons(self):
        self.back_action.setEnabled(self.history_index > 0)
        self.fwd_action.setEnabled(self.history_index < len(self.history) - 1)
