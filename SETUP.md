# Worship Songs Presenter - Setup Guide

## Project Structure

```
worship_songs_presenter/
├── app/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py      # Application configuration
│   │   └── defaults.json  # Default settings
│   ├── resources/         # Icons, images, etc.
│   ├── ui/                # User interface components
│   │   ├── dialogs/       # Dialog windows
│   │   ├── widgets/       # Custom widgets
│   │   └── windows/       # Main application windows
│   └── utils/             # Utility functions
├── config/
│   └── app_logo.png      # Application logo
├── data/                 # Application data
│   ├── lyrics/           # Lyrics files
│   ├── temp/             # Temporary files
│   └── videos/           # Background videos
├── main.py               # Application entry point
└── requirements.txt      # Python dependencies
```

## Setup Instructions

1. **Create required directories**:
   ```bash
   mkdir -p data/lyrics data/temp data/videos
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Add some videos**:
   - Place your background video files in the `data/videos/` directory
   - Or use the built-in YouTube downloader to fetch videos

## Running the Application

```bash
python main.py
```

## Configuration

Edit `app/config/defaults.json` to customize default settings like:
- Font size and color
- Animation duration
- Default video URLs
- Application name and version

## Troubleshooting

1. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Missing Directories**:
   - Ensure all required directories exist (data/lyrics, data/temp, data/videos)
   - The application will try to create them automatically

3. **Logo Not Found**:
   - Place your logo at `config/app_logo.png`
   - The application will work without it, but the splash screen will be blank
