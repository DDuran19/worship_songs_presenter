# Worship Lyrics Presenter

A professional presentation tool designed for worship teams to display lyrics and videos during church services. This application allows you to manage and present song lyrics alongside background videos or images, with customizable text styles and smooth animations.

## Features

- 🎤 **Lyrics Display**: Show song lyrics in a clean, customizable interface
- 🎥 **Video Backgrounds**: Play background videos from local files or YouTube
- 🎨 **Customizable Text**: Adjust font size, color, and style to match your worship theme
- 🖥️ **Dual Display Support**: Presenter view on one screen, lyrics on another
- ⚡ **Quick Navigation**: Easily switch between songs during service
- 🎚️ **Animation Controls**: Smooth fade transitions between slides

## Requirements

- Python 3.7 or higher
- PyQt5
- OpenCV
- PyTube
- youtube_dl

## Installation

1. Clone this repository:
   ```bash
   git clone [your-repository-url]
   cd lyrics
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Adding Songs**:
   - Place your lyrics files in the `lyrics` directory
   - Add video files to the `videos` directory or use YouTube URLs

2. **Running the Application**:
   ```bash
   python app.py
   ```

3. **Controls**:
   - **Spacebar**: Play/Pause video
   - **Left/Right Arrows**: Navigate between slides
   - **Escape**: Exit fullscreen
   - **F11**: Toggle fullscreen
   - **Ctrl+Q**: Quit application

## Customization

You can customize the appearance by modifying the `config/defaults.json` file:

```json
{
    "font_size": 48,
    "font_color": "white",
    "margins": [50, 0, 50, 0],
    "italic": false,
    "fade_duration": 0.5
}
```

## Directory Structure

```
.
├── app.py                # Main application file
├── config/               # Configuration files
│   └── defaults.json     # Default settings
├── lyrics/               # Store your lyrics files here
├── videos/               # Store local video files here
├── JSGC_logo.png         # Application logo
└── requirements.txt      # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE). You are free to use, modify, and distribute this software for any purpose, including commercial use, as long as the original copyright and license notice are included.

## Support

For support, please open an issue in the GitHub repository.
