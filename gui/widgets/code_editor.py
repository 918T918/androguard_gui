from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal
from androguard.decompiler.dad.decompile import DvClass, DvMethod
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import HtmlFormatter

class DecompilerThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, obj, dx, is_method=False):
        super().__init__()
        self.obj = obj
        self.dx = dx
        self.is_method = is_method
        
    def run(self):
        try:
            if not self.dx:
                self.finished.emit("Analysis object (dx) not available.")
                return
            
            if self.is_method:
                dv = DvMethod(self.obj, self.dx)
            else:
                dv = DvClass(self.obj, self.dx)
                
            dv.process()
            self.finished.emit(dv.get_source())
        except Exception as e:
            self.finished.emit(f"Decompilation failed: {e}")

class CodeEditorTab(QWidget):
    def __init__(self, class_obj, is_method=False, dx=None):
        super().__init__()
        self.class_obj = class_obj
        self.dx = dx
        self.is_method = is_method
        
        self.setup_ui()
        self.load_code()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        
        self.loading_label = QLabel("Decompiling...")
        layout.addWidget(self.loading_label)
        
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        self.editor.hide()
        
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_code(self):
        if self.dx:
            self.thread = DecompilerThread(self.class_obj, self.dx, self.is_method)
            self.thread.finished.connect(self.on_decompile_finished)
            self.thread.start()
        else:
            self.loading_label.setText("No analysis object available. Cannot decompile.")

    def on_decompile_finished(self, source):
        self.loading_label.hide()
        
        try:
            formatter = HtmlFormatter(style='colorful', full=True, noclasses=True)
            html_content = highlight(source, JavaLexer(), formatter)
            self.editor.setHtml(html_content)
        except Exception:
            self.editor.setPlainText(source)
            
        self.editor.show()
