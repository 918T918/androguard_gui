from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont

class HexViewer(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setup_ui()
        self.load_hex()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_hex(self):
        out = []
        chunk_size = 16
        for i in range(0, len(self.data), chunk_size):
            chunk = self.data[i:i+chunk_size]
            
            offset = f"{i:08x}  "
            
            hex_bytes = " ".join(f"{b:02x}" for b in chunk)
            hex_bytes = hex_bytes.ljust(48)
            
            ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            
            out.append(f"{offset}{hex_bytes} | {ascii_chars}")
            
            if i > 100000:
                out.append("... [Truncated for performance] ...")
                break
                
        self.editor.setPlainText("\n".join(out))