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
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtGui import QPixmap

# Import MainWindow from _app.py
from _app import MainWindow, SplashScreen

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
    setup_logging()
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set application information
    app.setApplicationName("Worship Songs Presenter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Worship Team")
    
    # Create and show the splash screen
    splash = SplashScreen()
    splash.show()
    
    # Process events to make sure the splash screen is shown
    app.processEvents()
    
    try:
        # Create the main window
        window = MainWindow()
        
        # Ensure get_styled_input always returns a tuple (text, ok)
        original_get_styled_input = window.get_styled_input
        
        def safe_get_styled_input(*args, **kwargs):
            result = original_get_styled_input(*args, **kwargs)
            if result is None:
                return "", False
            if isinstance(result, tuple) and len(result) == 2:
                return result
            return "", False
            
        window.get_styled_input = safe_get_styled_input
        
        # Close the splash screen and show the main window
        splash.close_splash()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        # Log any errors that occur during startup
        logging.critical("Application failed to start", exc_info=True)
        QMessageBox.critical(
            None,
            "Startup Error",
            f"The application failed to start due to an error:\n{str(e)}\n\n"
            "Please check the logs for more information."
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
