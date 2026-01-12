from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter

class ResourceViewer(QWidget):
    def __init__(self, apk):
        super().__init__()
        self.apk = apk
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
            # Get resources.arsc decoded as XML
            # Some versions of androguard provide get_resources_as_xml or similar
            # Alternatively, we can iterate through the ResourceTable
            r = self.apk.get_resources()
            if not r:
                self.editor.setPlainText("No resources found.")
                return
            
            # This is a bit complex in Androguard to get one giant XML.
            # Usually we want to see specific resource files.
            # For now, let's list the basic public resources.
            out = ["<!-- Decoded Resources -->\n<resources>"]
            
            for package in r.get_packages_names():
                for type_name in r.get_types(package):
                    for res in r.get_resources(package, type_name):
                        out.append(f'  <item type="{type_name}" name="{res.get_name()}">{res.get_value()}</item>')
            
            out.append("</resources>")
            xml_str = "\n".join(out)
            
            formatter = HtmlFormatter(style='colorful', full=True, noclasses=True)
            html_content = highlight(xml_str, XmlLexer(), formatter)
            self.editor.setHtml(html_content)
            
        except Exception as e:
            self.editor.setPlainText(f"Error decoding resources: {e}")
