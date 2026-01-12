from PyQt6.QtWidgets import (QMainWindow, QScrollArea, QLabel, QMessageBox, 
                             QWidget, QVBoxLayout, QPushButton)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import tempfile
import os
import subprocess

# We can use internal tools or just export basic blocks manually.
# A simpler way is to use androguard's ability to create dot files if available, 
# or manually traverse basic blocks.

class CFGWindow(QMainWindow):
    def __init__(self, method, analysis):
        super().__init__()
        self.setWindowTitle(f"CFG: {method.get_name()}")
        self.resize(800, 600)
        self.method = method
        self.analysis = analysis # Analysis object
        
        self.setup_ui()
        self.generate_graph()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.image_label = QLabel("Generating Graph...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.image_label)
        
        layout.addWidget(self.scroll)
        
        # Zoom controls could go here

    def generate_graph(self):
        try:
            # Get MethodAnalysis
            method_analysis = self.analysis.get_method(self.method)
            if not method_analysis:
                self.image_label.setText("No analysis for this method.")
                return

            # Create DOT source
            # We can use built-in androguard functions or build minimal dot
            # method_analysis.get_basic_blocks() returns BasicBlocks
            
            dot_content = "digraph CFG {\nnode [shape=box];\n"
            
            for bb in method_analysis.get_basic_blocks():
                # Node
                label = f"Offset: {bb.start:x}\n"
                # Add instructions? Too long. Just offsets for now.
                # Or first instruction.
                ins = list(bb.get_instructions())
                if ins:
                    label += str(ins[0].get_name())
                    
                dot_content += f'"{bb.name}" [label="{label}"];\n'
                
                # Edges
                for child in bb.childs:
                    dot_content += f'"{bb.name}" -> "{child[2].name}";\n'
            
            dot_content += "}"
            
            # Write to temp file
            tmp_dot = tempfile.mktemp(suffix=".dot")
            tmp_png = tempfile.mktemp(suffix=".png")
            
            with open(tmp_dot, "w") as f:
                f.write(dot_content)
                
            # Run dot
            subprocess.check_call(["dot", "-Tpng", tmp_dot, "-o", tmp_png])
            
            # Load Image
            pixmap = QPixmap(tmp_png)
            self.image_label.setPixmap(pixmap)
            self.image_label.resize(pixmap.size())
            
            # Cleanup
            os.remove(tmp_dot)
            os.remove(tmp_png)
            
        except Exception as e:
            self.image_label.setText(f"Error generating graph: {e}")
            import traceback
            traceback.print_exc()
