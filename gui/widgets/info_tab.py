from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QScrollArea, QGroupBox
from PyQt6.QtCore import Qt

class InfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.form_layout = QFormLayout()
        content_widget.setLayout(self.form_layout)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        self.form_layout.addRow(QLabel("Load an APK to see details."))

    def update_info(self, apk):
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.add_section("General Information")
        self.add_row("App Name", apk.get_app_name())
        self.add_row("Package Name", apk.get_package())
        self.add_row("Version Code", apk.get_androidversion_code())
        self.add_row("Version Name", apk.get_androidversion_name())
        self.add_row("Min SDK", apk.get_min_sdk_version())
        self.add_row("Target SDK", apk.get_target_sdk_version())
        
        self.add_section("Permissions")
        perms = apk.get_permissions()
        if perms:
            for p in perms:
                self.form_layout.addRow(QLabel(str(p)))
        else:
             self.form_layout.addRow(QLabel("No permissions found."))

        self.add_section("Activities")
        acts = apk.get_activities()
        if acts:
            for a in acts:
                self.form_layout.addRow(QLabel(str(a)))
        
        self.add_section("Services")
        srvs = apk.get_services()
        if srvs:
            for s in srvs:
                self.form_layout.addRow(QLabel(str(s)))

    def add_section(self, title):
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        self.form_layout.addRow(label)

    def add_row(self, label, value):
        self.form_layout.addRow(label + ":", QLabel(str(value)))
