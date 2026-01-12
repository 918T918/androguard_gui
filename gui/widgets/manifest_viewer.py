from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter

class ManifestViewer(QWidget):
    def __init__(self, apk, dark_mode=True):
        super().__init__()
        self.apk = apk
        self.dark_mode = dark_mode
        self.setup_ui()
        self.load_manifest()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Monospace", 10))
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def load_manifest(self):
        try:
            axml = self.apk.get_android_manifest_xml()
            if axml is not None:
                from lxml import etree
                xml_str = etree.tostring(axml, pretty_print=True, encoding='unicode')
                style = 'monokai' if self.dark_mode else 'colorful'
                formatter = HtmlFormatter(style=style, full=True, noclasses=True)
                html_content = highlight(xml_str, XmlLexer(), formatter)
                self.editor.setHtml(html_content)
            else:
                self.editor.setPlainText("Could not parse AndroidManifest.xml")
        except Exception as e:
            self.editor.setPlainText(f"Error loading manifest: {e}")