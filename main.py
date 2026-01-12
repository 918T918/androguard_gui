import sys
import logging
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Androguard GUI")
    app.setOrganizationName("Gemini")
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
