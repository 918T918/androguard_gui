from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter

class ResourceViewer(QWidget):
    def __init__(self, apk, dark_mode=True):
        super().__init__()
        self.apk = apk
        self.dark_mode = dark_mode
        self.setup_ui()
        self.load_resources()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_resources(self):
        try:
            r = self.apk.get_resources()
            if not r:
                self.editor.setPlainText("No resources found.")
                return
            out = ["<!-- Decoded Resources -->\n<resources>"]
            for package in r.get_packages_names():
                for type_name in r.get_types(package):
                    for res in r.get_resources(package, type_name):
                        out.append(f'  <item type="{type_name}" name="{res.get_name()}">{res.get_value()}</item>')
            out.append("</resources>")
            xml_str = "\n".join(out)
            style = 'monokai' if self.dark_mode else 'colorful'
            formatter = HtmlFormatter(style=style, full=True, noclasses=True)
            html_content = highlight(xml_str, XmlLexer(), formatter)
            self.editor.setHtml(html_content)
        except Exception as e:
            self.editor.setPlainText(f"Error decoding resources: {e}")