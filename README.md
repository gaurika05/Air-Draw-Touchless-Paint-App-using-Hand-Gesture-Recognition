# Air Draw - Touchless Paint App (v1.0.0)

A virtual drawing application that lets you paint in the air using hand gestures. Built with Python, OpenCV, and MediaPipe for hand tracking.

## Current Features (v1.0.0)

- Real-time hand gesture tracking using MediaPipe
- Draw in the air using your index finger
- Multiple color options (Blue, Green, Red, Yellow)
- Eraser functionality
- Save drawings to file
- Clear canvas option
- User-friendly interface with color selection boxes

## Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- NumPy

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/air_draw.git
cd air_draw
```

2. Create and activate virtual environment (recommended):
```bash
python -m venv air_venv
source air_venv/bin/activate  # On Windows: air_venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Controls:
- Use your index finger to draw
- Use index and middle fingers to select colors/eraser
- Press 'c' to clear the canvas
- Press 's' to save your drawing
- Press 'q' to quit

## Upcoming Features

Future versions will include:
- Additional drawing tools
- More color options
- Brush size adjustment
- Advanced gesture controls
- Image overlay support
- Custom canvas sizes

## Credits

Based on the implementation by [gaurika05](https://github.com/gaurika05/Air-Draw-Touchless-Paint-App-using-Hand-Gesture-Recognition)

## Version History

### v1.0.0
- Initial release
- Basic drawing functionality
- Color selection
- Eraser tool
- Save/Clear options 