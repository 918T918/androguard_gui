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
                # Use full=False to get just the HTML fragment
                formatter = HtmlFormatter(style=style, full=False, noclasses=True)
                html_content = highlight(xml_str, XmlLexer(), formatter)
                
                # Wrap in a div with the correct background color to avoid white bars
                bg_color = "#2b2b2b" if self.dark_mode else "#ffffff"
                text_color = "#d3d3d3" if self.dark_mode else "#000000"
                styled_html = f"<div style='background-color: {bg_color}; color: {text_color};'>{html_content}</div>"
                
                self.editor.setHtml(styled_html)
            else:
                self.editor.setPlainText("Could not parse AndroidManifest.xml")
        except Exception as e:
            self.editor.setPlainText(f"Error loading manifest: {e}")
