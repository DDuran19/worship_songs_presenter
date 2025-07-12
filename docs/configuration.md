# Configuration Reference

## Default Settings

The application stores its configuration in `config/defaults.json`. This file is automatically created with default values if it doesn't exist.

### Available Settings

#### Display Settings
```json
{
  "font_size": 48,              // Base font size in pixels
  "font_color": "white",        // Text color (CSS color name or hex code)
  "italic": false,              // Whether to use italic font
  "show_next_line": false,      // Show the next lyric line
  "fade_duration": 0.5,         // Transition duration in seconds
  "margins": [50, 0, 50, 0]     // Left, Top, Right, Bottom margins in pixels
}
```

#### Video Settings
```json
{
  "default_volume": 80,         // Initial volume (0-100)
  "loop_video": true,           // Loop video playback
  "mute_audio": false,          // Mute video audio by default
  "youtube_quality": "1080p"    // Preferred YouTube video quality
}
```

#### Application Settings
```json
{
  "auto_save": true,           // Auto-save changes
  "check_updates": true,       // Check for updates on startup
  "recent_files": [],          // List of recently opened files
  "window_geometry": null      // Saved window size and position
}
```

## Environment Variables

You can override certain settings using environment variables:

- `LYRICS_DIR`: Custom directory for lyrics files
- `VIDEOS_DIR`: Custom directory for video files
- `CONFIG_DIR`: Custom directory for configuration files

Example:
```bash
export LYRICS_DIR=/path/to/custom/lyrics
export VIDEOS_DIR=/path/to/custom/videos
python _app.py
```

## Command Line Arguments

The application supports the following command line arguments:

```
usage: _app.py [-h] [--no-splash] [--debug] [--reset-config] [song_file]

positional arguments:
  song_file       Path to a song file to open on startup

optional arguments:
  -h, --help      show this help message and exit
  --no-splash     Disable the splash screen
  --debug         Enable debug mode
  --reset-config  Reset configuration to defaults
```

## Custom Themes

You can create custom themes by adding a CSS file to the `themes` directory. The application will automatically detect and load all `.css` files from this directory.

Example theme file (`themes/dark.css`):
```css
QMainWindow, QDialog {
    background-color: #2b2b2b;
    color: #e0e0e0;
}

QListWidget {
    background-color: #3c3f41;
    color: #e0e0e0;
    border: 1px solid #555;
}

/* Add more styles as needed */
```

## Keyboard Shortcuts

### Global Shortcuts
- `Ctrl+Q`: Quit application
- `F1`: Show help
- `F11`: Toggle fullscreen
- `Esc`: Exit fullscreen

### Presentation Mode
- `Space`: Play/Pause video
- `Left/Right Arrows`: Previous/Next slide
- `Up/Down Arrows`: Volume control
- `M`: Toggle mute
- `F`: Toggle fullscreen
- `Esc`: Exit presentation mode

## File Formats

### Lyrics Files
Lyrics files should be in plain text format with the `.txt` extension. Use blank lines to separate slides.

Example:
```
Verse 1
Amazing grace, how sweet the sound
That saved a wretch like me

Chorus
Amazing grace, how sweet the sound
That saved a wretch like me
```

### Video Files
Supported video formats:
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)

## Troubleshooting

### Common Issues

1. **Videos don't play**
   - Ensure you have the necessary codecs installed
   - Try converting the video to a different format
   - Check file permissions

2. **YouTube videos don't load**
   - Check your internet connection
   - The video might be restricted or removed
   - Try a different video quality setting

3. **Application crashes on startup**
   - Try resetting the configuration with `--reset-config`
   - Check the error log in the application directory
   - Reinstall the application

### Logs
Logs are stored in the application directory:
- Windows: `%APPDATA%\WorshipLyricsPresenter\logs`
- macOS: `~/Library/Logs/WorshipLyricsPresenter`
- Linux: `~/.local/share/WorshipLyricsPresenter/logs`

## Updating

To update the application:

1. Backup your configuration and data
2. Pull the latest changes:
   ```bash
   git pull origin main
   ```
3. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Restart the application
