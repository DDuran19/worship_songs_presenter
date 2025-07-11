import os
import json
import time
import logging
import traceback
from pathlib import Path
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer, QUrl

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidgetItem, QLabel, QMenu, QMessageBox, QStyle, QFileDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QSize, pyqtSlot
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

from app.config import config
from app.ui.windows.splash_screen import SplashScreen
from app.ui.windows.presenter_window import PresenterWindow
from app.ui.dialogs import (
    SettingsDialog, StyledInputDialog, RenameVideoDialog
)
from app.ui.widgets import TopBar, LyricsList, VideoControls

# Paths from config
LYRICS_DIR = config["paths"]["lyrics"]
VIDEOS_DIR = config["paths"]["videos"]
CONFIG_DIR = Path(__file__).parents[2] / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"

class MainWindow(QMainWindow):
    """Main application window for Worship Songs Presenter."""
    def __init__(self, show_splash=True):
        # Initialize QMainWindow first
        super().__init__()
        logging.info("Initializing MainWindow...")
        
        # Initialize instance variables
        self.show_splash = show_splash
        self.splash = None
        self.presenter = None
        self.defaults = {}
        self._initialized = False
        self.worker = None
        self.songs = []
        self.default_video_urls = []
        self._current_file = None
        self._song_metadata = {
            'title': 'Untitled',
            'artist': '',
            'key': 'C',
            'tempo': 120,
            'lyrics': '',
            'chords': {}
        }
        
        try:
            # Set up logging
            self._setup_logging()
            
            # Set up the basic UI
            logging.info("Setting up basic UI...")
            self._setup_ui()
            
            # Show splash screen if needed
            if self.show_splash:
                logging.info("Showing splash screen...")
                self.splash = SplashScreen()
                self.splash.show()
                QApplication.processEvents()
            
            # Use a single-shot timer to load data after the event loop starts
            QTimer.singleShot(100, self._delayed_init)
            logging.info("MainWindow initialization complete, scheduled delayed init")
            
        except Exception as e:
            logging.error(f"Error during MainWindow initialization: {e}", exc_info=True)
            QMessageBox.critical(None, "Initialization Error", 
                               f"Failed to initialize application: {str(e)}\n\nCheck logs for details.")
    
    def _setup_ui(self):
        """Set up the main UI components"""
        self.setup_window_properties()
        self.setup_main_layout()
        self.setup_content_area()
    
    def setup_window_properties(self):
        """Configure window properties and appearance"""
        logging.info("Setting up window properties...")
        try:
            self.setWindowTitle(config["app"]["name"])
            
            # Try to load the app icon
            try:
                icon_path = Path(__file__).parent.parent.parent.parent / "config" / "app_logo.png"
                if icon_path.exists():
                    self.setWindowIcon(QIcon(str(icon_path)))
                else:
                    logging.warning(f"App icon not found at: {icon_path}")
            except Exception as e:
                logging.warning(f"Could not load app icon: {e}")
            
            self.setWindowFlags(Qt.Window)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                }
            """)
            
            # Set minimum size
            self.setMinimumSize(1024, 768)
            
            # Center the window on screen
            self.center()
            
        except Exception as e:
            logging.error(f"Error setting up window properties: {e}")
            raise
    
    def center(self):
        """Center the window on the screen"""
        try:
            # Get the screen geometry
            screen = QApplication.primaryScreen().geometry()
            
            # Get the window geometry
            window_geometry = self.frameGeometry()
            
            # Calculate center position
            x = (screen.width() - window_geometry.width()) // 2
            y = (screen.height() - window_geometry.height()) // 2
            
            # Move the window to the center
            self.move(x, y)
            
        except Exception as e:
            logging.warning(f"Could not center window: {e}")
    
    def setup_main_layout(self):
        """Set up the main window layout"""
        try:
            logging.info("Setting up main layout...")
            
            # Create central widget and main layout
            central_widget = QWidget()
            central_widget.setObjectName("centralWidget")
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # Create main widget with styling
            self.main_widget = QWidget()
            self.main_widget.setObjectName("mainWidget")
            self.main_widget.setStyleSheet("""
                QWidget#mainWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                }
            """)
            
            main_layout.addWidget(self.main_widget)
            
        except Exception as e:
            logging.error(f"Error setting up main layout: {e}")
            raise
    
    def setup_content_area(self):
        """Set up the main content area with all widgets"""
        try:
            logging.info("Setting up content area...")
            
            # Main widget layout
            main_widget_layout = QVBoxLayout(self.main_widget)
            main_widget_layout.setContentsMargins(10, 10, 10, 10)
            main_widget_layout.setSpacing(10)
            
            # Create top bar
            self.top_bar = TopBar()
            main_widget_layout.addWidget(self.top_bar)
            
            # Content container for main content and video section
            self.content_container = QWidget()
            self.content_layout = QVBoxLayout(self.content_container)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.content_layout.setSpacing(0)
            
            # Main content area
            self.content = QWidget()
            self.content_layout.addWidget(self.content, 1)
            
            # Video section container
            self.video_section_container = QWidget()
            self.video_section_container.setVisible(True)
            self.content_layout.addWidget(self.video_section_container)
            
            # Add container to main layout
            main_widget_layout.addWidget(self.content_container, 1)
            
            # Set up the content area
            self.setup_ui_components()
            
        except Exception as e:
            logging.error(f"Error setting up content area: {e}")
            raise
    
    def setup_ui_components(self):
        """Set up all UI components"""
        try:
            logging.info("Setting up UI components...")
            
            # Set up content layout
            content_layout = QVBoxLayout(self.content)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(5)
            
            # Add your UI components here
            # For example:
            # self.lyrics_list = LyricsList()
            # content_layout.addWidget(self.lyrics_list)
            
            # Set up video controls
            self.video_controls = VideoControls()
            self.video_section_container.setLayout(QVBoxLayout())
            self.video_section_container.layout().addWidget(self.video_controls)
            
            # Initialize connections after all UI components are set up
            self.init_connections()
            
        except Exception as e:
            logging.error(f"Error setting up UI components: {e}")
            raise
    
    def init_connections(self):
        """Initialize all signal-slot connections"""
        try:
            logging.info("Initializing signal-slot connections...")
            
            # Connect top bar signals
            if hasattr(self, 'top_bar'):
                # File menu actions
                if hasattr(self.top_bar, 'action_new'):
                    self.top_bar.action_new.triggered.connect(self.new_song)
                if hasattr(self.top_bar, 'action_open'):
                    self.top_bar.action_open.triggered.connect(self.open_song)
                if hasattr(self.top_bar, 'action_save'):
                    self.top_bar.action_save.triggered.connect(self.save_song)
                if hasattr(self.top_bar, 'action_save_as'):
                    self.top_bar.action_save_as.triggered.connect(self.save_song_as)
                if hasattr(self.top_bar, 'action_exit'):
                    self.top_bar.action_exit.triggered.connect(self.close)
                
                # Edit menu actions
                if hasattr(self.top_bar, 'action_undo'):
                    self.top_bar.action_undo.triggered.connect(self.undo)
                if hasattr(self.top_bar, 'action_redo'):
                    self.top_bar.action_redo.triggered.connect(self.redo)
                if hasattr(self.top_bar, 'action_cut'):
                    self.top_bar.action_cut.triggered.connect(self.cut)
                if hasattr(self.top_bar, 'action_copy'):
                    self.top_bar.action_copy.triggered.connect(self.copy)
                if hasattr(self.top_bar, 'action_paste'):
                    self.top_bar.action_paste.triggered.connect(self.paste)
                
                # View menu actions
                if hasattr(self.top_bar, 'action_toggle_video'):
                    self.top_bar.action_toggle_video.triggered.connect(self.toggle_video_panel)
                
                # Help menu actions
                if hasattr(self.top_bar, 'action_about'):
                    self.top_bar.action_about.triggered.connect(self.show_about)
                if hasattr(self.top_bar, 'action_about_qt'):
                    self.top_bar.action_about_qt.triggered.connect(QApplication.aboutQt)
            
            # Connect video controls if available
            if hasattr(self, 'video_controls'):
                if hasattr(self.video_controls, 'play_pause_clicked'):
                    self.video_controls.play_pause_clicked.connect(self.toggle_play_pause)
                if hasattr(self.video_controls, 'stop_clicked'):
                    self.video_controls.stop_clicked.connect(self.stop_playback)
                if hasattr(self.video_controls, 'volume_changed'):
                    self.video_controls.volume_changed.connect(self.set_volume)
                if hasattr(self.video_controls, 'position_changed'):
                    self.video_controls.position_changed.connect(self.seek_video)
            
            logging.info("Signal-slot connections initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing connections: {e}", exc_info=True)
            raise
    
    # ===== Menu Action Handlers =====
    
    def new_song(self):
        """Create a new song"""
        try:
            logging.info("Creating new song...")
            
            # Check for unsaved changes
            if hasattr(self, '_current_file') and self._current_file:
                reply = QMessageBox.question(
                    self, 'New Song',
                    'Do you want to save changes to the current song?',
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save
                )
                
                if reply == QMessageBox.Save:
                    self.save_song()
                elif reply == QMessageBox.Cancel:
                    return
            
            # Reset the UI for a new song
            self._current_file = None
            self.setWindowTitle(f"{config['app']['name']} - Untitled")
            
            # Clear any existing content
            if hasattr(self, 'lyrics_editor'):
                self.lyrics_editor.clear()
            
            # Reset any song metadata
            self._song_metadata = {
                'title': 'Untitled',
                'artist': '',
                'key': 'C',
                'tempo': 120,
                'lyrics': '',
                'chords': {}
            }
            
            # Update UI to reflect new song
            self._update_ui_from_metadata()
            
            logging.info("New song created")
            
        except Exception as e:
            logging.error(f"Error creating new song: {e}", exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to create new song: {e}')
    
    def open_song(self):
        """Open an existing song"""
        try:
            # Check for unsaved changes
            if hasattr(self, '_current_file') and self._current_file:
                reply = QMessageBox.question(
                    self, 'Open Song',
                    'Do you want to save changes to the current song?',
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save
                )
                
                if reply == QMessageBox.Save:
                    self.save_song()
                elif reply == QMessageBox.Cancel:
                    return
            
            # Show file dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Open Song',
                str(LYRICS_DIR),
                'JSON Files (*.json);;All Files (*)'
            )
            
            if file_path:
                self._load_song_file(file_path)
                
        except Exception as e:
            logging.error(f"Error opening song: {e}", exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to open song: {e}')
    
    def _load_song_file(self, file_path):
        """Load song data from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                song_data = json.load(f)
            
            # Validate song data
            required_fields = ['title', 'lyrics']
            for field in required_fields:
                if field not in song_data:
                    raise ValueError(f"Invalid song file: missing required field '{field}'")
            
            # Update current file and metadata
            self._current_file = file_path
            self._song_metadata = song_data
            
            # Update UI
            self.setWindowTitle(f"{config['app']['name']} - {song_data.get('title', 'Untitled')}")
            self._update_ui_from_metadata()
            
            logging.info(f"Loaded song from {file_path}")
            
        except Exception as e:
            logging.error(f"Error loading song file {file_path}: {e}", exc_info=True)
            raise
    
    def save_song(self):
        """Save the current song"""
        try:
            if not hasattr(self, '_current_file') or not self._current_file:
                return self.save_song_as()
            
            self._update_metadata_from_ui()
            self._save_to_file(self._current_file)
            
        except Exception as e:
            logging.error(f"Error saving song: {e}", exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to save song: {e}')
    
    def save_song_as(self):
        """Save the current song with a new name"""
        try:
            # Show save file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                'Save Song As',
                str(LYRICS_DIR / f"{self._song_metadata.get('title', 'Untitled')}.json"),
                'JSON Files (*.json);;All Files (*)'
            )
            
            if file_path:
                # Ensure .json extension
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                
                self._update_metadata_from_ui()
                self._save_to_file(file_path)
                self._current_file = file_path
                self.setWindowTitle(f"{config['app']['name']} - {self._song_metadata.get('title', 'Untitled')}")
                
        except Exception as e:
            logging.error(f"Error saving song as: {e}", exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to save song: {e}')
    
    def _save_to_file(self, file_path):
        """Save song data to a file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._song_metadata, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Song saved to {file_path}")
            
        except Exception as e:
            logging.error(f"Error saving to file {file_path}: {e}", exc_info=True)
            raise
    
    def _update_metadata_from_ui(self):
        """Update song metadata from UI elements"""
        if hasattr(self, 'lyrics_editor'):
            self._song_metadata['lyrics'] = self.lyrics_editor.toPlainText()
        
        # Update other metadata from UI fields if they exist
        if hasattr(self, 'title_edit'):
            self._song_metadata['title'] = self.title_edit.text().strip()
        if hasattr(self, 'artist_edit'):
            self._song_metadata['artist'] = self.artist_edit.text().strip()
        if hasattr(self, 'key_edit'):
            self._song_metadata['key'] = self.key_edit.text().strip()
        if hasattr(self, 'tempo_edit'):
            try:
                self._song_metadata['tempo'] = int(self.tempo_edit.text())
            except (ValueError, AttributeError):
                pass
    
    def _update_ui_from_metadata(self):
        """Update UI elements from song metadata"""
        if hasattr(self, 'lyrics_editor'):
            self.lyrics_editor.setPlainText(self._song_metadata.get('lyrics', ''))
        
        # Update other UI fields if they exist
        if hasattr(self, 'title_edit'):
            self.title_edit.setText(self._song_metadata.get('title', 'Untitled'))
        if hasattr(self, 'artist_edit'):
            self.artist_edit.setText(self._song_metadata.get('artist', ''))
        if hasattr(self, 'key_edit'):
            self.key_edit.setText(str(self._song_metadata.get('key', 'C')))
        if hasattr(self, 'tempo_edit'):
            self.tempo_edit.setText(str(self._song_metadata.get('tempo', 120)))
    
    def undo(self):
        """Undo the last action"""
        try:
            if hasattr(self, 'lyrics_editor') and self.lyrics_editor.isUndoAvailable():
                self.lyrics_editor.undo()
                logging.debug("Undo action performed")
        except Exception as e:
            logging.warning(f"Error in undo: {e}")
    
    def redo(self):
        """Redo the last undone action"""
        try:
            if hasattr(self, 'lyrics_editor') and self.lyrics_editor.isRedoAvailable():
                self.lyrics_editor.redo()
                logging.debug("Redo action performed")
        except Exception as e:
            logging.warning(f"Error in redo: {e}")
    
    def cut(self):
        """Cut selected text"""
        try:
            if hasattr(self, 'lyrics_editor'):
                self.lyrics_editor.cut()
                logging.debug("Cut action performed")
        except Exception as e:
            logging.warning(f"Error in cut: {e}")
    
    def copy(self):
        """Copy selected text"""
        try:
            if hasattr(self, 'lyrics_editor'):
                self.lyrics_editor.copy()
                logging.debug("Copy action performed")
        except Exception as e:
            logging.warning(f"Error in copy: {e}")
    
    def paste(self):
        """Paste text from clipboard"""
        try:
            if hasattr(self, 'lyrics_editor'):
                self.lyrics_editor.paste()
                logging.debug("Paste action performed")
        except Exception as e:
            logging.warning(f"Error in paste: {e}")
    
    def toggle_video_panel(self, checked):
        """Toggle the visibility of the video panel"""
        logging.info(f"Toggle video panel: {checked}")
        if hasattr(self, 'video_section_container'):
            self.video_section_container.setVisible(checked)
    
    def show_about(self):
        """Show the about dialog"""
        logging.info("Showing about dialog")
        QMessageBox.about(
            self,
            "About Worship Songs Presenter",
            "Worship Songs Presenter\n\n"
            "A tool for managing and presenting worship songs\n"
            f"Version 1.0.0\n"
            "© 2025 Worship Team"
        )
    
    # ===== Video Control Handlers =====
    
    def _init_video_player(self):
        """Initialize the video player components"""
        try:
            # Create media player
            self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            
            # Create video widget
            self.video_widget = QVideoWidget()
            self.video_controls.layout().insertWidget(0, self.video_widget, 1)  # Add to layout with stretch
            
            # Set video output
            self.media_player.setVideoOutput(self.video_widget)
            
            # Connect media player signals
            self.media_player.stateChanged.connect(self._on_media_state_changed)
            self.media_player.positionChanged.connect(self._on_position_changed)
            self.media_player.durationChanged.connect(self._on_duration_changed)
            self.media_player.error.connect(self._on_media_error)
            
            # Initialize volume
            self.media_player.setVolume(50)  # Default volume
            
            logging.info("Video player initialized")
            
        except Exception as e:
            logging.error(f"Error initializing video player: {e}", exc_info=True)
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        try:
            if not hasattr(self, 'media_player'):
                self._init_video_player()
            
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                logging.debug("Playback paused")
            else:
                # If no media is loaded, try to load the first video
                if self.media_player.mediaStatus() == QMediaPlayer.NoMedia:
                    self._load_default_video()
                self.media_player.play()
                logging.debug("Playback started")
                
        except Exception as e:
            logging.error(f"Error toggling play/pause: {e}", exc_info=True)
    
    def _load_default_video(self):
        """Load the first available video from the default video directory"""
        try:
            video_dir = Path(config['paths'].get('videos', ''))
            if video_dir.exists() and video_dir.is_dir():
                # Look for common video file extensions
                video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
                for ext in video_extensions:
                    video_files = list(video_dir.glob(f'*{ext}'))
                    if video_files:
                        video_path = str(video_files[0])
                        self.load_video(video_path)
                        return True
            return False
        except Exception as e:
            logging.error(f"Error loading default video: {e}")
            return False
    
    def load_video(self, file_path):
        """Load a video file into the player"""
        try:
            if not hasattr(self, 'media_player'):
                self._init_video_player()
            
            media_content = QMediaContent(QUrl.fromLocalFile(file_path))
            self.media_player.setMedia(media_content)
            self.media_player.play()
            
            # Update video controls
            if hasattr(self, 'video_controls'):
                self.video_controls.set_duration(self.media_player.duration())
            
            logging.info(f"Loaded video: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading video {file_path}: {e}", exc_info=True)
            QMessageBox.critical(self, 'Error', f'Failed to load video: {e}')
            return False
    
    def stop_playback(self):
        """Stop video playback"""
        try:
            if hasattr(self, 'media_player'):
                self.media_player.stop()
                logging.debug("Playback stopped")
        except Exception as e:
            logging.error(f"Error stopping playback: {e}")
    
    def set_volume(self, volume):
        """Set the volume level (0-100)"""
        try:
            if hasattr(self, 'media_player'):
                self.media_player.setVolume(volume)
                logging.debug(f"Volume set to: {volume}")
        except Exception as e:
            logging.error(f"Error setting volume: {e}")
    
    def seek_video(self, position):
        """Seek to a specific position in the video"""
        try:
            if hasattr(self, 'media_player') and self.media_player.isSeekable():
                self.media_player.setPosition(position)
                logging.debug(f"Seeked to position: {position}ms")
        except Exception as e:
            logging.error(f"Error seeking video: {e}")
    
    def _on_media_state_changed(self, state):
        """Handle media player state changes"""
        try:
            if hasattr(self, 'video_controls'):
                if state == QMediaPlayer.PlayingState:
                    self.video_controls.set_playing(True)
                else:
                    self.video_controls.set_playing(False)
        except Exception as e:
            logging.error(f"Error handling media state change: {e}")
    
    def _on_position_changed(self, position):
        """Update position in video controls"""
        try:
            if hasattr(self, 'video_controls'):
                self.video_controls.set_position(position)
        except Exception as e:
            logging.error(f"Error updating position: {e}")
    
    def _on_duration_changed(self, duration):
        """Update duration in video controls"""
        try:
            if hasattr(self, 'video_controls'):
                self.video_controls.set_duration(duration)
        except Exception as e:
            logging.error(f"Error updating duration: {e}")
    
    def _on_media_error(self):
        """Handle media player errors"""
        try:
            error = self.media_player.errorString()
            logging.error(f"Media player error: {error}")
            QMessageBox.critical(self, 'Media Error', f'Media playback error: {error}')
        except Exception as e:
            logging.error(f"Error handling media error: {e}")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = Path(config['paths']['temp']) / 'logs'
        log_dir.mkdir(exist_ok=True, parents=True)
        log_file = log_dir / 'app.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logging.info("Logging initialized")
    
    def _delayed_init(self):
        """Initialize heavy operations after the UI is shown"""
        logging.info("Starting delayed initialization...")
        try:
            # Load config in the main thread (fast operation)
            try:
                logging.info(f"Loading config from {CONFIG_FILE}")
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.default_video_urls = config_data.get('default_video_urls', [])
                    logging.info(f"Loaded {len(self.default_video_urls)} default video URLs")
            except FileNotFoundError:
                logging.warning(f"Config file not found at {CONFIG_FILE}, using default settings")
                self.default_video_urls = []
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing config file: {e}")
                self.default_video_urls = []
            except Exception as e:
                logging.error(f"Unexpected error loading config: {e}", exc_info=True)
                self.default_video_urls = []
            
            # Initialize connections
            logging.info("Initializing connections...")
            try:
                self.init_connections()
                logging.info("Connections initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing connections: {e}", exc_info=True)
                raise
            
            # Load initial data in a background thread
            logging.info("Starting background data loading...")
            self._load_initial_data()
            
        except Exception as e:
            error_msg = f"Error during delayed initialization: {e}"
            logging.error(error_msg, exc_info=True)
            
            # Ensure we have a valid QApplication instance before showing message box
            app = QApplication.instance()
            if app is not None:
                QMessageBox.critical(
                    None,  # No parent to avoid potential issues
                    "Initialization Error",
                    f"Failed to initialize application: {error_msg}\n\nCheck logs for details."
                )
            else:
                print(f"CRITICAL: {error_msg}", file=sys.stderr)
                
            # If we have a splash screen, ensure it's closed
            if hasattr(self, 'splash') and self.splash:
                try:
                    self.splash.close()
                except:
                    pass
    
    def _load_initial_data(self):
        """Load initial data in a background thread"""
        logging.info("Preparing to load initial data...")
        try:
            # Show loading indicator
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage("Loading data...")
            
            # Create and configure the worker
            logging.info("Creating worker thread for data loading...")
            self.worker = Worker(self._load_data)
            self.worker.signals.finished.connect(self._on_data_loaded)
            
            # Handle worker errors
            self.worker.finished.connect(lambda: logging.info("Worker thread finished"))
            self.worker.finished.connect(self.worker.deleteLater)
            
            # Start the worker
            logging.info("Starting worker thread...")
            self.worker.start()
            logging.info("Worker thread started successfully")
            
        except Exception as e:
            error_msg = f"Failed to start data loading: {e}"
            logging.error(error_msg, exc_info=True)
            self.statusBar().showMessage("Error loading data", 5000)
    
    def _load_data(self):
        """Method to be run in a worker thread"""
        logging.info("Background data loading started...")
        start_time = time.time()
        
        try:
            # Load songs
            songs = []
            logging.info(f"Loading songs from directory: {LYRICS_DIR}")
            
            if not os.path.exists(LYRICS_DIR):
                logging.warning(f"Lyrics directory does not exist: {LYRICS_DIR}")
                os.makedirs(LYRICS_DIR, exist_ok=True)
                logging.info(f"Created lyrics directory: {LYRICS_DIR}")
                return {'songs': []}
            
            song_files = [f for f in os.listdir(LYRICS_DIR) if f.endswith('.json')]
            logging.info(f"Found {len(song_files)} song files to process")
            
            for i, fn in enumerate(song_files, 1):
                try:
                    file_path = os.path.join(LYRICS_DIR, fn)
                    logging.debug(f"Loading song {i}/{len(song_files)}: {file_path}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        song_data = json.load(f)
                        
                    if not isinstance(song_data, dict):
                        logging.warning(f"Invalid song data in {fn}, expected dictionary")
                        continue
                        
                    if 'title' not in song_data:
                        logging.warning(f"Song in {fn} is missing title, skipping")
                        continue
                        
                    songs.append(song_data)
                    
                except json.JSONDecodeError as e:
                    logging.error(f"Error parsing JSON in {fn}: {e}")
                except PermissionError as e:
                    logging.error(f"Permission denied reading {fn}: {e}")
                except Exception as e:
                    logging.error(f"Unexpected error loading {fn}: {e}", exc_info=True)
            
            # Sort songs by title
            logging.info(f"Sorting {len(songs)} songs...")
            songs.sort(key=lambda s: s.get('title', '').lower())
            
            elapsed = time.time() - start_time
            logging.info(f"Successfully loaded {len(songs)} songs in {elapsed:.2f} seconds")
            
            return {
                'songs': songs,
                'load_time': elapsed
            }
            
        except Exception as e:
            error_msg = f"Critical error in data loading: {e}"
            logging.error(error_msg, exc_info=True)
            return {
                'error': error_msg,
                'traceback': str(traceback.format_exc())
            }
    
    def _on_data_loaded(self, result):
        """Called when background loading is complete"""
        logging.info("Processing loaded data...")
        
        try:
            # Check for errors in the result
            if 'error' in result:
                error_msg = result.get('error', 'Unknown error')
                traceback_info = result.get('traceback', 'No traceback available')
                logging.error(f"Error in background loading: {error_msg}\n{traceback_info}")
                raise Exception(f"Background loading failed: {error_msg}")
            
            # Update UI with loaded data
            self.songs = result.get('songs', [])
            load_time = result.get('load_time', 0)
            
            logging.info(f"Updating UI with {len(self.songs)} songs (load time: {load_time:.2f}s)")
            
            # Update song select dropdown
            if hasattr(self, 'top_bar') and hasattr(self.top_bar, 'song_select'):
                try:
                    song_titles = [s.get('title', 'Untitled') for s in self.songs]
                    logging.debug(f"Adding {len(song_titles)} songs to dropdown")
                    
                    # Block signals while updating to prevent unnecessary events
                    self.top_bar.song_select.blockSignals(True)
                    self.top_bar.song_select.clear()
                    self.top_bar.song_select.addItems(song_titles)
                    self.top_bar.song_select.blockSignals(False)
                    
                    logging.debug("Song dropdown updated successfully")
                    
                except Exception as e:
                    logging.error(f"Error updating song dropdown: {e}", exc_info=True)
                    raise
            
            # Mark as initialized
            self._initialized = True
            logging.info("Application initialization complete")
            
            # Hide splash screen if shown
            if hasattr(self, 'splash') and self.splash:
                try:
                    logging.info("Closing splash screen...")
                    self.splash.finish(self)
                    self.splash = None
                except Exception as e:
                    logging.error(f"Error closing splash screen: {e}", exc_info=True)
            
            # Ensure main window is shown
            if not self.isVisible():
                logging.info("Showing main window...")
                self.show()
                self.raise_()
                self.activateWindow()
            
            # Update status bar
            if hasattr(self, 'statusBar'):
                try:
                    msg = f"Ready - {len(self.songs)} songs loaded"
                    if load_time > 0.1:  # Only show load time if significant
                        msg += f" in {load_time:.1f}s"
                    self.statusBar().showMessage(msg, 5000)
                except Exception as e:
                    logging.error(f"Error updating status bar: {e}")
            
            logging.info("Application ready")
                
        except Exception as e:
            error_msg = f"Error finalizing initialization: {e}"
            logging.error(error_msg, exc_info=True)
            
            # Ensure we have a valid QApplication instance before showing message box
            app = QApplication.instance()
            if app is not None:
                QMessageBox.critical(
                    None,  # No parent to avoid potential issues
                    "Initialization Error",
                    f"Failed to load application data: {error_msg}\n\n"
                    "The application may not function correctly.\n"
                    "Please check the logs for more details."
                )
            
            # If we have a splash screen, ensure it's closed
            if hasattr(self, 'splash') and self.splash:
                try:
                    self.splash.close()
                except:
                    pass
            
            # Still try to show the main window in a degraded state
            if not self.isVisible():
                self.show()


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    finished = pyqtSignal(dict)  # Send back the result as a dictionary


class Worker(QThread):
    """Worker thread for running background tasks."""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        """Run the worker function and emit the result."""
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result if isinstance(result, dict) else {'result': result})
        except Exception as e:
            self.signals.finished.emit({'error': str(e)})
        
    def init_ui(self):
        """Initialize the main window UI components"""
        self.setup_window_properties()
        self.setup_directories()
        self.load_initial_settings()
        self.setup_main_layout()
        self.setup_content_area()
        
        # Show the window when initialization is complete
        if self.splash:
            self.splash.finish(self)
            self.setWindowOpacity(1.0)
        
    def setup_window_properties(self):
        """Configure window properties and appearance"""
        self.setWindowTitle(config["app"]["name"])
        self.setWindowIcon(QIcon(str(CONFIG_DIR / "app_logo.png")))
        self.setWindowFlags(Qt.Window)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
        # Show splash screen if enabled
        if self.show_splash:
            self.splash = SplashScreen()
            self.splash.show()
            QApplication.processEvents()
            # Don't show main window until splash is done
            self.setWindowOpacity(0.0)
        
    def setup_directories(self):
        """Ensure required directories exist"""
        if self.splash:
            self.splash.set_status("Checking directories...")
        os.makedirs(LYRICS_DIR, exist_ok=True)
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        
    def load_initial_settings(self):
        """Load application settings and initialize components"""
        if self.splash:
            self.splash.set_status("Loading settings...")
        self.defaults = self.load_settings()
        
        if self.splash:
            self.splash.set_status("Preparing presenter...")
        self.presenter = PresenterWindow()
        self.destroyed.connect(self.cleanup)
        
    def setup_main_layout(self):
        """Set up the main window layout"""
        # Create central widget and main layout
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create main widget with styling
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        
        main_layout.addWidget(self.main_widget)
        
    def setup_content_area(self):
        """Set up the main content area with all widgets"""
        # Main widget layout
        main_widget_layout = QVBoxLayout(self.main_widget)
        main_widget_layout.setContentsMargins(10, 10, 10, 10)
        main_widget_layout.setSpacing(10)
        
        # Content container for main content and video section
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Main content area
        self.content = QWidget()
        self.content_layout.addWidget(self.content, 1)
        
        # Video section container
        self.video_section_container = QWidget()
        self.video_section_container.setVisible(True)
        self.content_layout.addWidget(self.video_section_container)
        
        # Add container to main layout
        main_widget_layout.addWidget(self.content_container, 1)
        
        # Set up the content area
        self.setup_ui_components()
        
    def setup_ui_components(self):
        """Set up all UI components"""
        # Content layout
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Top bar
        self.top_bar = TopBar()
        content_layout.addWidget(self.top_bar)
        
        # Lyrics list
        self.lyrics_list = LyricsList()
        content_layout.addWidget(self.lyrics_list, 1)
        
        # Video controls
        self.video_controls = VideoControls()
        self.video_section_container.setLayout(QVBoxLayout())
        self.video_section_container.layout().addWidget(self.video_controls)
        
    def add_lyrics(self):
        """Handle adding a new song to the library"""
        # Get the song title from the user
        title, ok = self.get_styled_input(
            "Add New Song",
            "Enter song title:",
            ""
        )
        
        if ok and title.strip():
            # Create a new song entry
            song = {
                "title": title.strip(),
                "lyrics": [{"text": "", "section": "Verse 1"}],
                "sections": ["Verse 1"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save the song to a file
            song_file = os.path.join(LYRICS_DIR, f"{title.lower().replace(' ', '_')}.json")
            try:
                with open(song_file, 'w', encoding='utf-8') as f:
                    json.dump(song, f, indent=2, ensure_ascii=False)
                
                # Refresh the UI to show the new song
                self.refresh_ui()
                
                # Select the new song
                index = self.top_bar.song_select.findText(title)
                if index >= 0:
                    self.top_bar.song_select.setCurrentIndex(index)
                    
                # Show success message
                QMessageBox.information(
                    self,
                    "Success",
                    f"Song '{title}' has been added successfully.",
                    QMessageBox.Ok
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save song: {str(e)}",
                    QMessageBox.Ok
                )
    
    def init_connections(self):
        """Initialize all signal-slot connections"""
        # Connect top bar signals
        self.top_bar.connect_signals({
            'on_song_changed': lambda idx: self.on_song(idx),
            'on_add_song': self.add_lyrics,
            'on_settings': self.open_settings,
            'on_refresh': self.refresh_ui,
            'on_toggle_focus': self.toggle_focus_mode,
            'on_toggle_presenter': self.toggle_presenter_mode
        })
        
        # Connect lyrics list signals
        self.lyrics_list.connect_signals(
            self.show_context_menu,
            lambda: self.new_slide(self.top_bar.current_index())
        )
        
        # Connect video controls signals
        self.video_controls.connect_signals(
            self.add_video,
            lambda idx: self.on_video(idx)
        )

        # Finalize UI
        self.resize(1000, 700)
        self.center()
        self.load_settings()
        self.refresh_ui()
        self.presenter.visibilityChanged.connect(self.on_presenter_visibility_changed)

        if self.splash:
            QTimer.singleShot(1000, lambda: self._show_main())
        else:
            self.show()

    def _show_main(self):
        self.close_splash()
        self.show()
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def center(self):
        frame_geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def cleanup(self):
        if hasattr(self, 'presenter') and self.presenter:
            self.presenter.close()
            self.presenter = None

    def close_splash(self):
        if hasattr(self, 'splash') and self.splash:
            self.splash.close_splash()
            self.splash = None

    def closeEvent(self, event):
        self.cleanup()
        event.accept()

    def toggle_focus_mode(self):
        self.video_section_container.setVisible(self.focus_btn.isChecked())

    def toggle_presenter_mode(self, checked):
        if checked:
            self.presenter.show()
            self.start_btn.setText("■ Stop Presenting")
        else:
            self.presenter.hide()
            self.start_btn.setText("▶ Start Presenting")

    def on_presenter_visibility_changed(self, visible):
        self.start_btn.setChecked(visible)
        self.start_btn.setText("■ Stop Presenting" if visible else "▶ Start Presenting")
        if visible:
            if not hasattr(self, 'normal_size'):
                self.normal_size = self.size()
            screen = QApplication.primaryScreen().availableGeometry()
            new_height = int(screen.height() * 0.7)
            self.resize(self.width(), new_height)
            self.center()
        elif hasattr(self, 'normal_size'):
            self.resize(self.normal_size)
            self.center()

    def refresh_ui(self):
        self.load_songs()
        self.load_videos()

    def open_settings(self):
        dlg = SettingsDialog(self, self.defaults)
        if dlg.exec_() == QDialogButtonBox.Ok:
            vals = dlg.get_values()
            json.dump(vals, open(CONFIG_FILE, 'w', encoding='utf-8'), indent=2)
            self.defaults = vals
            self.presenter.apply_style()

    def load_settings(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        settings = {
            'window_geometry': None,
            'window_state': None,
            'recent_files': [],
            'default_font': 'Arial',
            'default_font_size': 16
        }
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings.update(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")
        return settings

    def save_settings(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.defaults, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_songs(self):
        """Load all songs from the lyrics directory and populate the song select dropdown"""
        self.songs = []
        
        # Ensure the lyrics directory exists
        os.makedirs(LYRICS_DIR, exist_ok=True)
        
        # Load all JSON files in the lyrics directory
        for fn in os.listdir(LYRICS_DIR):
            if fn.endswith('.json'):
                try:
                    with open(os.path.join(LYRICS_DIR, fn), 'r', encoding='utf-8') as f:
                        self.songs.append(json.load(f))
                except (json.JSONDecodeError, PermissionError) as e:
                    print(f"Error loading {fn}: {e}")
        
        # Sort songs by title
        self.songs.sort(key=lambda s: s.get('title', '').lower())
        
        # Update the song select dropdown
        if hasattr(self, 'top_bar') and hasattr(self.top_bar, 'song_select'):
            current_text = self.top_bar.song_select.currentText()
            self.top_bar.song_select.clear()
            self.top_bar.song_select.addItems([s.get('title', 'Untitled') for s in self.songs])
            
            # Restore the previous selection if possible
            if current_text:
                index = self.top_bar.song_select.findText(current_text)
                if index >= 0:
                    self.top_bar.song_select.setCurrentIndex(index)

    def rename_video(self):
        item = self.video_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Rename Video", "Please select a video first.")
            return
            
        old_path = item.data(Qt.UserRole)
        new_base, ok = RenameVideoDialog.get_new_video_name(old_path, self)
        
        if not ok or not new_base.strip():
            return
            
        if hasattr(self.presenter, 'cap') and self.presenter.cap:
            self.presenter.cap.release()
            
        # Get the file extension from the old path
        ext = os.path.splitext(old_path)[1]
        new_path = os.path.join(VIDEOS_DIR, new_base.strip() + ext)
        
        try:
            os.rename(old_path, new_path)
            self.refresh_ui()
        except OSError as e:
            QMessageBox.critical(self, "Rename Error", f"Could not rename file: {e}")

    def get_styled_input(self, title, label, text='', parent=None):
        """
        Get styled text input from the user.
        
        Args:
            title (str): Dialog window title
            label (str): Label text for the input field
            text (str, optional): Default text to display. Defaults to ''.
            parent (QWidget, optional): Parent widget. Defaults to None.
            
        Returns:
            tuple: (entered_text, success)
        """
        multi_line = 'lyric' in title.lower()
        return StyledInputDialog.get_text_input(
            title, label, text, parent or self, multi_line
        )

    def on_song(self, idx, section_filter=None):
        """Handle song selection and display lyrics with section filtering."""
        if idx == -1:
            self.lyrics_list.clear()
            return
            
        self.lyrics_list.clear()
        song = self.songs[idx]
        
        # Get all sections for this song
        sections = set()
        for slide in song['lyrics']:
            if 'section' in slide and slide['section']:
                sections.add(slide['section'])
        
        # Clear existing section buttons
        for i in reversed(range(self.section_layout.count())): 
            widget = self.section_layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()
        
        # Add "All" button
        all_btn = QPushButton("All")
        all_btn.setCheckable(True)
        all_btn.setChecked(section_filter is None)
        all_btn.clicked.connect(lambda: self.on_song(idx, None))
        all_btn.setStyleSheet("""
            QPushButton {
                padding: 2px 8px;
                font-size: 11px;
                border-radius: 3px;
                border: 1px solid #dee2e6;
                background: #f8f9fa;
            }
            QPushButton:checked {
                background: #4a90e2;
                color: white;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
        """)
        self.section_layout.insertWidget(0, all_btn)
        
        # Add section buttons
        for i, section in enumerate(sorted(sections), 1):
            btn = QPushButton(section or "No Section")
            btn.setCheckable(True)
            btn.setChecked(section == section_filter)
            btn.clicked.connect(lambda checked, s=section: self.on_song(idx, s))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 8px;
                    font-size: 11px;
                    border-radius: 3px;
                    border: 1px solid #dee2e6;
                    background: #f8f9fa;
                }
                QPushButton:checked {
                    background: #4a90e2;
                    color: white;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            self.section_layout.insertWidget(i, btn)
        
        # Add stretch to push buttons to the left
        self.section_layout.addStretch(1)
        
        # Add lyrics to the list
        current_section = None
        for i, slide in enumerate(song['lyrics']):
            # Skip if section filter is active and doesn't match
            if section_filter is not None and slide.get('section') != section_filter:
                continue
                
            # Check if section changed
            if 'section' in slide and slide['section'] != current_section:
                current_section = slide['section']
                # Add section header
                section_item = QListWidgetItem()
                section_item.setFlags(Qt.NoItemFlags)
                section_item.setSizeHint(QSize(0, 24))
                
                section_widget = QLabel(f"<b>{current_section or 'No Section'}</b>")
                section_widget.setStyleSheet("""
                    background-color: #f1f3f5;
                    padding: 2px 8px;
                    border-radius: 2px;
                    margin: 1px 0;
                    font-size: 12px;
                """)
                
                self.lyrics_list.addItem(section_item)
                self.lyrics_list.setItemWidget(section_item, section_widget)
            
            # Add the lyric item
            item = QListWidgetItem(slide['text'])
            item.setData(Qt.UserRole, slide)
            self.lyrics_list.addItem(item)
            
            # Apply alternating background for sections
            if i % 2 == 0:
                item.setBackground(QColor(250, 250, 250))
            else:
                item.setBackground(QColor(255, 255, 255))
        
        # Connect the double click handler for the lyric item
        def on_double_clicked(item):
            data = item.data(Qt.UserRole)
            if isinstance(data, dict):
                self.presenter.set_lyric(data['text'])
        
        self.lyrics_list.itemDoubleClicked.connect(on_double_clicked)
        
        # Update presenter with song title if not filtering by section
        if section_filter is None:
            self.presenter.set_lyric(song['title'])
    
    def new_slide(self, song_idx, section=''):
        if song_idx == -1:
            return ''
            
        song = self.songs[song_idx]
        
        # Determine section filter
        section_filter = None
        for i in range(self.section_layout.count()):
            widget = self.section_layout.itemAt(i).widget()
            if widget and widget.isChecked() and widget.text() != "All":
                section_filter = widget.text() or ''
                break
                
        # Get section from user
        sect, ok = self.get_styled_input('Add New Lyric', 'Section (optional):')
        if not ok:
            return section_filter or ''
            
        # Get lyric text from user
        txt, ok = self.get_styled_input('Add New Lyric', 'Lyric text:')
        if ok and txt:
            song['lyrics'].append({'text': txt, 'section': sect or None})
            self.save_song(song_idx)
            self.on_song(song_idx)
            return sect or ''
            
        return section_filter or ''

    def edit_slide(self, song_idx, idx):
        if song_idx < 0 or idx < 0:
            return
        song = self.songs[song_idx]
        actual = [s for s in song['lyrics'] if 'text' in s][idx]
        sect, _ = self.get_styled_input('Edit Lyric', 'Section:', actual.get('section') or '')
        txt, ok = self.get_styled_input('Edit Lyric', 'Lyric text:', actual['text'])
        if ok and txt:
            actual.update({'text': txt, 'section': sect or None})
            self.save_song(song_idx)
            self.on_song(song_idx)

    def save_song(self, idx):
        title = self.songs[idx]['title']
        path = os.path.join(LYRICS_DIR, f"{title}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.songs[idx], f, indent=2)

    def get_video_thumbnail(self, video_path):
        thumbs = os.path.join(VIDEOS_DIR, '.thumbnails')
        os.makedirs(thumbs, exist_ok=True)
        name = os.path.splitext(os.path.basename(video_path))[0] + '.jpg'
        thumb_path = os.path.join(thumbs, name)
        if not os.path.exists(thumb_path):
            try:
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (160, 90))
                    cv2.imwrite(thumb_path, frame)
                cap.release()
            except Exception:
                return None
        return thumb_path

    def load_videos(self):
        """Load all videos from the videos directory and populate the video controls"""
        if not hasattr(self, 'video_controls') or not hasattr(self.video_controls, 'video_list'):
            return
            
        # Ensure the videos directory exists
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        
        # Clear the current video list
        self.video_controls.video_list.clear()
        
        # Add each video file to the list
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')
        for fn in os.listdir(VIDEOS_DIR):
            if fn.lower().endswith(video_extensions):
                item = QListWidgetItem(fn)
                item.setData(Qt.UserRole, os.path.join(VIDEOS_DIR, fn))
                self.video_controls.video_list.addItem(item)

    def sanitize_filename(self, filename):
        import re
        filename = re.sub(r'[\\/:*?"<>|]', ' ', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        return filename[:200] or 'video'

    def download_video(self, url):
        """
        Download a YouTube video, naming the file after the video's title.
        Tries pytube first, then yt_dlp (Python API), then falls back to the yt-dlp CLI.
        """
        # Reset progress bar
        self.progress.setValue(0)
        
        # Function to get clean filename from title
        def get_clean_filename(yt):
            title = yt.title if hasattr(yt, 'title') else 'video'
            return f"{self.sanitize_filename(title)}.mp4"

        # 1) Try pytube
        try:
            yt = YouTube(url, on_progress_callback=self._on_progress)
            stream = (
                yt.streams
                .filter(progressive=True, file_extension='mp4')
                .order_by('resolution')
                .desc()
                .first()
            )
            if stream:
                # Get sanitized filename
                filename = get_clean_filename(yt)
                output_path = os.path.join(VIDEOS_DIR, filename)
                
                # Download to a temporary file first
                temp_path = output_path + '.download'
                stream.download(filename=temp_path, skip_existing=False)
                
                # Rename to final filename
                if os.path.exists(temp_path):
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(temp_path, output_path)
                    print(f"Downloaded: {output_path}")
                    self.refresh_ui()
                    return
        except Exception as e:
            print(f"pytube failed: {e}")

        # 2) Try yt_dlp (Python API)
        try:
            def ydl_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        self.progress.setValue(int(d['downloaded_bytes'] / d['total_bytes'] * 100))
                elif d['status'] == 'finished':
                    self.progress.setValue(100)
                    
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(VIDEOS_DIR, '%(title)s.%(ext)s'),
                'progress_hooks': [ydl_hook],
                'noplaylist': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    # Sanitize the filename
                    safe_title = self.sanitize_filename(info.get('title', 'video'))
                    output_path = os.path.join(VIDEOS_DIR, f"{safe_title}.mp4")
                    ydl.params['outtmpl'] = output_path
                    ydl.download([url])
                    self.refresh_ui()
                    return
        except Exception as e:
            print(f"yt_dlp (Python) failed: {e}")

        # 3) Fall back to yt-dlp CLI if available
        try:
            import subprocess
            import tempfile
            
            # First get video info to get the title
            info_cmd = [
                "yt-dlp",
                "--skip-download",
                "--print-json",
                "--no-warnings",
                url
            ]
            
            result = subprocess.run(info_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                safe_title = self.sanitize_filename(info.get('title', 'video'))
                output_path = os.path.join(VIDEOS_DIR, f"{safe_title}.mp4")
                
                # Now download with the sanitized filename
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                    "--no-playlist",
                    "--output", output_path,
                    "--newline",
                    "--no-warnings",
                    url,
                ]
                
                # Run with progress updates
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Process output for progress updates
                for line in process.stdout:
                    if '[download]' in line and '%' in line:
                        # Extract percentage from lines like: [download]  12.3% of 10.00MiB at 1.23MiB/s ETA 00:07
                        try:
                            percent = float(line.split('%')[0].split()[-1])
                            self.progress.setValue(int(percent))
                        except (ValueError, IndexError):
                            pass
                
                process.wait()
                if process.returncode == 0 and os.path.exists(output_path):
                    self.progress.setValue(100)
                    self.refresh_ui()
                    return
                
        except Exception as e:
            QMessageBox.critical(self, "Download Error", f"Failed to download video: {str(e)}")
        finally:
            # Clean up any temporary files
            temp_files = [f for f in os.listdir(VIDEOS_DIR) if f.endswith('.download') or f.endswith('.part')]
            for f in temp_files:
                try:
                    os.remove(os.path.join(VIDEOS_DIR, f))
                except:
                    pass
            
            # Refresh UI whether download succeeded or not
            self.refresh_ui()


    def _on_progress(self, stream, chunk, remaining):
        total = stream.filesize
        self.progress.setValue(int((total - remaining) / total * 100))

    @pyqtSlot(dict)
    def _ydl_hook(self, d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or 1
            self.progress.setValue(int((total - d.get('bytes_remaining', 0)) / total * 100))
        elif d.get('status') == 'finished':
            self.progress.setValue(100)

    def add_video(self):
        """Handle adding a new video from URL"""
        if not hasattr(self, 'video_controls') or not hasattr(self.video_controls, 'video_url'):
            return
            
        url = self.video_controls.video_url.text().strip()
        if url:
            self.download_video(url)
            # Clear the URL field after starting download
            self.video_controls.video_url.clear()

    def show_context_menu(self, pos):
        item = self.lyrics_list.itemAt(pos)
        if not item or not (item.flags() & Qt.ItemIsSelectable):
            return
        menu = QMenu()
        edit = menu.addAction("Edit")
        delete = menu.addAction("Delete")
        song_idx = self.song_select.currentIndex()
        lyric_idx = sum(1 for i in range(self.lyrics_list.row(item)+1)
                        if self.lyrics_list.item(i).flags() & Qt.ItemIsSelectable) - 1
        edit.triggered.connect(lambda: self.edit_slide(song_idx, lyric_idx))
        delete.triggered.connect(lambda: self.del_slide(song_idx, lyric_idx))
        menu.exec_(self.lyrics_list.viewport().mapToGlobal(pos))

    def on_lyric_double_clicked(self, item):
        data = item.data(Qt.UserRole)
        if isinstance(data, dict):
            self.presenter.set_lyric(data['text'])

    def on_video(self, idx):
        path = self.video_list.item(idx).data(Qt.UserRole)
        self.presenter.set_video(path)
