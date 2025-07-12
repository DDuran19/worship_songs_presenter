# User Guide

## Getting Started

### Installation
1. Ensure you have Python 3.7 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the necessary directories if they don't exist:
   ```
   mkdir lyrics videos config
   ```

### First Run
1. Launch the application:
   ```bash
   python _app.py
   ```
2. The application will create default configuration files if they don't exist

## Basic Usage

### Adding Songs
1. Click the "Add Song" button
2. Enter the song title and lyrics
3. Optionally, add a background video by selecting a file or pasting a YouTube URL

### Presenting
1. Select a song from the list
2. Click "Start Presenting" or press F5
3. Use the following controls during presentation:
   - **Spacebar**: Play/Pause video
   - **Left/Right Arrows**: Navigate between slides
   - **Escape**: Exit fullscreen
   - **F11**: Toggle fullscreen

## Features

### Lyrics Management
- Add, edit, and delete songs
- Organize songs into sections
- Import/Export lyrics in various formats

### Video Playback
- Support for local video files
- YouTube video integration
- Playback controls
- Loop and autoplay options

### Display Settings
- Customize font size, color, and style
- Adjust text alignment and margins
- Set background color or image
- Configure transitions and animations

## Tips
- Use the "Focus Mode" to hide the video section when not needed
- Save frequently used settings as presets
- Use keyboard shortcuts for faster navigation
- The application auto-saves your work, but it's good practice to back up your lyrics files regularly

## Troubleshooting
- If videos don't play, ensure you have the necessary codecs installed
- For YouTube videos, check your internet connection
- If the application crashes, check the error logs in the application directory
- Make sure you have write permissions in the application directory
