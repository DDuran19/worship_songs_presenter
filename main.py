"""
Main entry point for Worship Songs Presenter application.
"""
import os
import sys
import logging
import traceback
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import PyQt after setting up paths
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QStyle
from PyQt5.QtCore import Qt, QCoreApplication, QTimer, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QIcon

from app.ui.windows.main_window import MainWindow
from app.ui.windows.splash_screen import SplashScreen

def setup_logging():
    """Configure application logging."""
    try:
        # Ensure logs directory exists
        log_dir = BASE_DIR / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'app.log'
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,  # More verbose logging during development
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Set up logger for this module
        logger = logging.getLogger(__name__)
        logger.info("Logging initialized")
        logger.info(f"Log file: {log_file}")
        
        return log_file
        
    except Exception as e:
        print(f"Failed to set up logging: {e}")
        # Fallback to basic console logging
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to configure file logging: {e}")
        return None

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupts to be processed normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical("Uncaught exception:", 
                    exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error message to user
    error_msg = f"""
    An unexpected error occurred:
    
    {str(exc_value)}
    
    Check the log file for more details.
    """
    
    # Use a basic message box if QApplication is running
    app = QApplication.instance()
    if app is not None:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            error_msg
        )
    else:
        print(error_msg, file=sys.stderr)

def main():
    """Main application entry point."""
    # Set up logging
    log_file = setup_logging()
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application information
    app.setApplicationName("Worship Songs Presenter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Worship Team")
    
    try:
        # Create and show the main window with splash screen
        main_window = MainWindow(show_splash=True)
        
        # Fade in the main window if it was hidden
        if main_window.windowOpacity() < 1.0:
            fade_in = QPropertyAnimation(main_window, b"windowOpacity")
            fade_in.setDuration(300)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.start()
        
        # Show the main window
        main_window.show()
        
        # Enter the application event loop
        result = app.exec_()
        
        # Clean up resources
        if hasattr(main_window, 'cleanup'):
            main_window.cleanup()
            
        return result
        
    except Exception as e:
        logging.error(f"Error starting application: {e}", exc_info=True)
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")
        return 1

if __name__ == '__main__':
    main()
