from flask import Flask, render_template, Response
import cv2
from main import initialize_air_draw
import os
import atexit

app = Flask(__name__)

# Initialize the Air Draw system
air_draw = None

@app.route('/')
def index():
    return render_template('index.html')

def cleanup():
    global air_draw
    if air_draw is not None:
        air_draw.cleanup()

atexit.register(cleanup)

def gen_frames():
    global air_draw
    try:
        if air_draw is None:
            air_draw = initialize_air_draw()
        
        while True:
            frame = air_draw.get_frame()
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(f"Error in gen_frames: {e}")
        cleanup()
        yield b''

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 