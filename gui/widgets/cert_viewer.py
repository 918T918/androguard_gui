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
            # Newer androguard might return a generator or a slightly different list
            certs = list(self.apk.get_certificates())
            if not certs:
                self.editor.setPlainText("No certificates found.")
                return
                
            out = []
            for i, cert in enumerate(certs):
                out.append(f"Certificate #{i}")
                out.append("-" * 20)
                
                # Use getattr to be safe with different androguard versions
                def get_val(obj, attr):
                    val = getattr(obj, attr, "N/A")
                    if callable(val):
                        try: val = val()
                        except: val = "N/A"
                    return str(val)

                # Issuer/Subject might be objects with human_friendly or just strings
                issuer = getattr(cert, 'issuer', None)
                if hasattr(issuer, 'human_friendly'):
                    out.append(f"Issuer: {issuer.human_friendly}")
                else:
                    out.append(f"Issuer: {str(issuer)}")

                subject = getattr(cert, 'subject', None)
                if hasattr(subject, 'human_friendly'):
                    out.append(f"Subject: {subject.human_friendly}")
                else:
                    out.append(f"Subject: {str(subject)}")

                out.append(f"Serial: {get_val(cert, 'serial_number')}")
                out.append(f"Algorithm: {get_val(cert, 'signature_algo')}")
                out.append(f"Valid From: {get_val(cert, 'not_before')}")
                out.append(f"Valid Until: {get_val(cert, 'not_after')}")
                out.append(f"SHA1: {get_val(cert, 'sha1_fingerprint')}")
                out.append(f"SHA256: {get_val(cert, 'sha256_fingerprint')}")
                out.append("\n")
                
            self.editor.setPlainText("\n".join(out))
        except Exception as e:
            self.editor.setPlainText(f"Error loading certificates: {e}")
            import traceback
            traceback.print_exc()
