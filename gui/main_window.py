from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QFileDialog, QToolBar, QStatusBar, QMessageBox, QDockWidget, QMenu, QApplication, QProgressBar, QTextEdit)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont
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
from gui.widgets.smali_viewer import SmaliViewer
from gui.widgets.resource_viewer import ResourceViewer
from gui.widgets.scanner_tab import ScannerTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Androguard GUI")
        self.resize(1200, 800)
        
        self.settings = QSettings("Gemini", "AndroguardGUI")
        self.apk_path = None
        
        self.dark_mode = self.settings.value("darkMode", "True") == "True"
        
        self.analysis_thread = None
        self.dx = None
        
        self.history = []
        self.history_index = -1
        self.navigating = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.apply_theme()
        
    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget, QDockWidget, QDialog {
                    background-color:
                    color:
                }
                QTabWidget::pane { border: 1px solid
                QTabBar::tab { background:
                QTabBar::tab:selected { background:
                QTreeWidget, QListWidget, QTextEdit, QPlainTextEdit, QTableWidget, QLineEdit {
                    background-color:
                    color:
                    border: 1px solid
                }
                QMenuBar, QMenu, QToolBar {
                    background-color:
                    color:
                }
                QMenu::item:selected { background-color:
                QPushButton {
                    background-color:
                    color:
                    border: 1px solid
                    padding: 5px;
                }
                QPushButton:hover { background-color:
                QStatusBar { background:
            """)
        else:
            self.setStyleSheet("")
            
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("darkMode", str(self.dark_mode))
        self.apply_theme()

    def setup_ui(self):
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(True)
        self.central_tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.central_tabs)
        
        self.tree_dock = QDockWidget("Project Structure", self)
        self.tree_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.project_tree = ProjectTree()
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.open_tree_context_menu)
        self.project_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_dock.setWidget(self.project_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tree_dock)
        
        self.info_tab = InfoTab()
        self.central_tabs.addTab(self.info_tab, "Dashboard")
        
        self.log_dock = QDockWidget("Log Console", self)
        self.log_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Monospace", 9))
        self.log_dock.setWidget(self.log_console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(15)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        menubar = self.menuBar()
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
        
        device_menu = menubar.addMenu("&Device")
        list_packages_action = QAction("&List Packages...", self)
        list_packages_action.triggered.connect(self.open_device_dialog)
        device_menu.addAction(list_packages_action)
        
        search_menu = menubar.addMenu("&Search")
        search_action = QAction("&Search Symbols...", self)
        search_action.setShortcut("Ctrl+Shift+F")
        search_action.triggered.connect(self.open_search_dialog)
        search_menu.addAction(search_action)
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)

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
        
        toolbar.addSeparator()
        theme_action = QAction("Toggle Dark Mode", self)
        theme_action.triggered.connect(self.toggle_dark_mode)
        toolbar.addAction(theme_action)

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        recent_files = self.settings.value("recentFiles", [])
        if not recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return
        for path in recent_files:
            action = QAction(path, self)
            action.triggered.connect(self._make_recent_loader(path))
            self.recent_menu.addAction(action)

    def _make_recent_loader(self, path):
        return lambda: self.load_apk(path)

    def add_to_recent_files(self, path):
        recent_files = self.settings.value("recentFiles", [])
        if not isinstance(recent_files, list): recent_files = []
        if path in recent_files: recent_files.remove(path)
        recent_files.insert(0, path)
        recent_files = recent_files[:10]
        self.settings.setValue("recentFiles", recent_files)
        self.update_recent_files_menu()

    def export_to_java(self):
        if not self.dx:
            QMessageBox.warning(self, "Export", "Analyze an APK first.")
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if not out_dir: return
        from core.exporter import ExportThread
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Exporting classes...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        self.export_thread = ExportThread(self.dx, out_dir)
        self.export_thread.progress.connect(lambda m: progress.setLabelText(f"Exporting: {m}"))
        self.export_thread.finished.connect(lambda: (progress.cancel(), QMessageBox.information(self, "Export", "Export Complete!")))
        self.export_thread.start()

    def open_apk_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open APK", "", "APK Files (*.apk);;All Files (*)")
        if file_name: self.load_apk(file_name)

    def open_device_dialog(self):
        dialog = DeviceDialog(self)
        if dialog.exec():
            if dialog.selected_apk_path: self.load_apk(dialog.selected_apk_path)

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
        self.log_console.append(f"<b>Loading {path}...</b>")
        self.status_bar.showMessage(f"Loading {path}...")
        self.project_tree.clear()
        self.history = []; self.history_index = -1; self.update_nav_buttons()
        while self.central_tabs.count() > 1: self.central_tabs.removeTab(1)
        
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        self.analysis_thread = AnalysisThread(path)
        self.analysis_thread.finished.connect(self.on_analysis_finished)
        self.analysis_thread.progress.connect(self.on_analysis_progress)
        self.analysis_thread.error.connect(self.on_analysis_error)
        self.analysis_thread.start()
        self.project_tree.setEnabled(False)

    def on_analysis_progress(self, msg, val):
        self.status_bar.showMessage(msg)
        self.log_console.append(f"[*] {msg}")
        self.progress_bar.setValue(val)

    def on_analysis_finished(self, apk, classes, dex):
        self.status_bar.showMessage("Analysis Complete")
        self.log_console.append("<font color='green'><b>[+] Analysis Complete!</b></font>")
        self.progress_bar.hide()
        self.dx = dex 
        self.project_tree.setEnabled(True)
        self.project_tree.populate(apk, classes, dex)
        self.info_tab.update_info(apk)
        self.manifest_view = ManifestViewer(apk, dark_mode=self.dark_mode)
        self.central_tabs.insertTab(1, self.manifest_view, "Manifest")
        self.res_view = ResourceViewer(apk, dark_mode=self.dark_mode)
        self.central_tabs.addTab(self.res_view, "Resources")
        self.scanner_view = ScannerTab(dex)
        self.scanner_view.methodSelected.connect(lambda m: self.open_code_tab(m, is_method=True))
        self.central_tabs.addTab(self.scanner_view, "Security Scan")
        self.files_view = FilesView(apk)
        self.files_view.fileSelected.connect(self.open_hex_tab)
        self.central_tabs.addTab(self.files_view, "Files")
        self.cert_view = CertViewer(apk)
        self.central_tabs.addTab(self.cert_view, "Certificates")
        self.strings_view = StringsView(dex)
        self.strings_view.stringClicked.connect(self.open_method_from_string)
        self.central_tabs.addTab(self.strings_view, "Strings")

    def on_analysis_error(self, msg):
        self.status_bar.showMessage(f"Error: {msg}")
        self.log_console.append(f"<font color='red'><b>[!] Error: {msg}</b></font>")
        self.progress_bar.hide()
        QMessageBox.critical(self, "Error", f"Failed to analyze APK:\n{msg}")
        self.project_tree.setEnabled(True)

    def open_method_from_string(self, method_obj): self.open_code_tab(method_obj, is_method=True)

    def open_hex_tab(self, path, data):
        name = str(f"Hex: {os.path.basename(path)}")
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        viewer = HexViewer(data)
        self.central_tabs.addTab(viewer, name)
        self.central_tabs.setCurrentWidget(viewer)

    def on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data: return
        if data['type'] == 'class': self.open_code_tab(data['obj'], is_method=False)
        elif data['type'] == 'method': self.open_code_tab(data['obj'], is_method=True)

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
            action_smali = menu.addAction("View Smali Bytecode")
            action_frida = menu.addAction("Generate Frida Hook")
            action = menu.exec(self.project_tree.viewport().mapToGlobal(position))
            if action == action_xref: self.show_xrefs(method_obj)
            elif action == action_cfg: self.show_cfg(method_obj)
            elif action == action_smali: self.open_smali_tab(method_obj)
            elif action == action_frida: self.generate_frida_hook(method_obj)

    def show_xrefs(self, method_obj):
        if not self.dx: return
        ma = self.dx.get_method(method_obj)
        if not ma:
            QMessageBox.information(self, "XRefs", "No analysis data for this method.")
            return
        xrefs = list(ma.get_xref_from())
        if not xrefs:
            QMessageBox.information(self, "XRefs", "No references found.")
            return
        dialog = XRefDialog(self, xrefs)
        if dialog.exec(): self.open_code_tab(dialog.selected_method, is_method=True)

    def show_cfg(self, method_obj):
        if not self.dx: return
        self.cfg_window = CFGWindow(method_obj, self.dx)
        self.cfg_window.show()

    def open_smali_tab(self, method_obj):
        name = str(f"Smali: {method_obj.get_name()}")
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        viewer = SmaliViewer(method_obj)
        self.central_tabs.addTab(viewer, name)
        self.central_tabs.setCurrentWidget(viewer)

    def generate_frida_hook(self, method_obj):
        class_name = method_obj.get_class_name()[1:-1].replace('/', '.')
        method_name = method_obj.get_name()
        lines = [
            "Java.perform(function() {",
            f"    var targetClass = Java.use('{class_name}');",
            f"    targetClass.{method_name}.overload(...).implementation = function() {{",
            f"        console.log('[*] {method_name} called!');",
            f"        var ret = this.{method_name}.apply(this, arguments);",
            f"        console.log('[*] {method_name} returns: ' + ret);",
            "        return ret;",
            "    };",
            "});"
        ]
        hook = "\\n".join(lines)
        QApplication.clipboard().setText(hook)
        self.status_bar.showMessage("Frida hook copied to clipboard!")
        QMessageBox.information(self, "Frida Hook", "Frida hook snippet has been copied to your clipboard.")

    def open_code_tab(self, obj, is_method=False):
        if not self.navigating: self.add_history(obj, is_method)
        name = str(obj.get_name() if hasattr(obj, 'get_name') else str(obj))
        for i in range(self.central_tabs.count()):
            if self.central_tabs.tabText(i) == name:
                self.central_tabs.setCurrentIndex(i)
                return
        editor = CodeEditorTab(obj, is_method, dx=self.dx, dark_mode=self.dark_mode)
        self.central_tabs.addTab(editor, name)
        self.central_tabs.setCurrentWidget(editor)

    def close_tab(self, index): self.central_tabs.removeTab(index)
    def add_history(self, obj, is_method):
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