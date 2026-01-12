from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont

class SmaliViewer(QWidget):
    def __init__(self, method_obj):
        super().__init__()
        self.method_obj = method_obj
        self.setup_ui()
        self.load_smali()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_smali(self):
        try:
            out = []
            # method_obj is EncodedMethod
            out.append(f".method {self.method_obj.get_access_flags_string()} {self.method_obj.get_name()}{self.method_obj.get_descriptor()}")
            
            code = self.method_obj.get_code()
            if code:
                for ins in code.get_instructions():
                    out.append(f"    {ins.get_name()} {ins.get_output()}")
            
            out.append(".end method")
            self.editor.setPlainText("\n".join(out))
        except Exception as e:
            self.editor.setPlainText(f"Error loading Smali: {e}")
