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
            formatter = HtmlFormatter(style=style, full=False, noclasses=True)
            html_content = highlight(xml_str, XmlLexer(), formatter)
            
            bg_color = "#2b2b2b" if self.dark_mode else "#ffffff"
            text_color = "#d3d3d3" if self.dark_mode else "#000000"
            styled_html = f"<div style='background-color: {bg_color}; color: {text_color};'>{html_content}</div>"
            
            self.editor.setHtml(styled_html)
        except Exception as e:
            self.editor.setPlainText(f"Error decoding resources: {e}")
