from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont

class CertViewer(QWidget):
    def __init__(self, apk):
        super().__init__()
        self.apk = apk
        self.setup_ui()
        self.load_certs()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_certs(self):
        try:
            certs = self.apk.get_certificates()
            if not certs:
                self.editor.setPlainText("No certificates found.")
                return
                
            out = []
            for i, cert in enumerate(certs):
                out.append(f"Certificate
                out.append("-" * 20)
                out.append(f"Issuer: {cert.issuer.human_friendly}")
                out.append(f"Subject: {cert.subject.human_friendly}")
                out.append(f"Serial: {cert.serial_number}")
                out.append(f"Algorithm: {cert.signature_algo}")
                out.append(f"Valid From: {cert.not_before}")
                out.append(f"Valid Until: {cert.not_after}")
                out.append(f"SHA1: {cert.sha1_fingerprint}")
                out.append(f"SHA256: {cert.sha256_fingerprint}")
                out.append("\n")
                
            self.editor.setPlainText("\n".join(out))
        except Exception as e:
            self.editor.setPlainText(f"Error loading certificates: {e}")
