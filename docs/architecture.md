# Application Architecture

## Overview
The Worship Lyrics Presenter is built using Python with PyQt5 for the user interface and OpenCV for video processing. The application follows a modular architecture with clear separation of concerns between the UI, business logic, and data management.

## Main Components

### 1. Core Modules
- `_app.py`: Main application file containing the GUI and core functionality
- `presenter.py`: Handles the presentation window and display logic
- `settings.py`: Manages application settings and configuration
- `lyrics_manager.py`: Handles loading and managing song lyrics
- `video_manager.py`: Manages video playback and processing

### 2. Data Directory Structure
```
.
├── config/           # Configuration files
│   └── defaults.json # Default application settings
├── lyrics/           # Lyrics files (one per song)
├── videos/           # Background video files
└── docs/             # Documentation
```

### 3. UI Components
- **MainWindow**: Primary application window with song list and controls
- **PresenterWindow**: Full-screen display for lyrics and videos
- **SettingsDialog**: Configuration interface for application settings
- **SplashScreen**: Initial loading screen

## Data Flow
1. User interacts with the MainWindow to select songs and configure settings
2. Selected lyrics and videos are loaded and prepared for presentation
3. PresenterWindow displays the content with the specified styling
4. User controls the presentation through keyboard shortcuts and UI controls
5. Settings are persisted to disk for future sessions

## Dependencies
- PyQt5: For the graphical user interface
- OpenCV: For video processing and display
- PyTube: For YouTube video integration
- youtube_dl: For video downloading functionality
