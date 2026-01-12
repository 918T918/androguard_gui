import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from gui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("androguard_gui.log")
    ]
)
logger = logging.getLogger("Main")

def exception_hook(exctype, value, tb):
    """Global exception handler to show a dialog instead of silent crash."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    logger.error(f"Uncaught exception:\n{error_msg}")
    
    if QApplication.instance():
        QMessageBox.critical(None, "Critical Error", 
                           f"An unexpected error occurred:\n{value}\n\nCheck androguard_gui.log for details.")
    sys.__excepthook__(exctype, value, tb)

def main():
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    app.setApplicationName("Androguard GUI")
    app.setOrganizationName("Gemini")
    
    try:
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
