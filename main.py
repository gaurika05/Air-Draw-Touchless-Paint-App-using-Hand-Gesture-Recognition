import cv2
import numpy as np
from hand_tracking import HandDetector
import os
import logging
import warnings

# Suppress MediaPipe and protobuf warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning)

# Force OpenCV to use X11 instead of Wayland
os.environ["QT_QPA_PLATFORM"] = "xcb"

def main():
    print("Initializing Air Draw...")
    print("Controls:")
    print("- Use index finger to draw")
    print("- Use index + middle fingers to select colors")
    print("- Press 'c' to clear canvas")
    print("- Press 's' to save drawing")
    print("- Press 'q' to quit")
    
    try:
        # Initialize video capture
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not open video capture device")
            
        cap.set(3, 1280)  # width
        cap.set(4, 720)   # height

        # Initialize hand detector
        detector = HandDetector(detection_confidence=0.85)

        # Drawing variables
        draw_color = (255, 0, 0)  # Default blue
        brush_thickness = 15
        eraser_thickness = 50
        is_eraser = False
        
        # Create canvas (white background)
        canvas = np.ones((720, 1280, 3), np.uint8) * 255
        
        # Create drawing layer (transparent)
        drawing_layer = np.zeros((720, 1280, 3), np.uint8)
        
        # Previous coordinates for drawing
        x_prev, y_prev = 0, 0
        
        # Color options (removed black)
        colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (0, 255, 255),  # Yellow
            (255, 255, 255) # Eraser
        ]
        
        # Color selection boxes - adjusted spacing for 5 options
        color_boxes = []
        for i, color in enumerate(colors):
            color_boxes.append([int(1280/6 * (i+1)), 0, int(1280/6 * (i+1) + 50), 50, color])

        while True:
            # Get image from webcam
            success, img = cap.read()
            if not success:
                print("Failed to get frame from camera")
                break
                
            img = cv2.flip(img, 1)  # Mirror image

            # Find hand landmarks
            img = detector.find_hands(img)
            landmark_list = detector.find_position(img)

            if landmark_list:
                # Index and middle finger coordinates
                x1, y1 = landmark_list[8][1:]  # Index finger tip
                x2, y2 = landmark_list[12][1:]  # Middle finger tip

                # Check which fingers are up
                fingers = []
                if y1 < landmark_list[6][2]:  # Index finger
                    fingers.append(1)
                if y2 < landmark_list[10][2]:  # Middle finger
                    fingers.append(1)

                # Selection Mode - Two fingers up
                if len(fingers) == 2:
                    # Check for color selection
                    for x, y, w, h, color in color_boxes:
                        if x < x1 < w and y < y1 < h:
                            if color == (255, 255, 255):  # Eraser
                                is_eraser = True
                                draw_color = color
                                brush_thickness = eraser_thickness
                            else:
                                is_eraser = False
                                draw_color = color
                                brush_thickness = 15
                    
                    # Draw selection boxes
                    for x, y, w, h, color in color_boxes:
                        cv2.rectangle(img, (x, y), (w, h), color, cv2.FILLED)
                        # Add black border to white eraser box for visibility
                        if color == (255, 255, 255):
                            cv2.rectangle(img, (x, y), (w, h), (0, 0, 0), 2)
                        if color == draw_color:
                            cv2.rectangle(img, (x, y), (w, h), (128, 128, 128), 3)

                    x_prev, y_prev = 0, 0  # Reset previous points

                # Drawing Mode - Index finger up
                elif len(fingers) == 1:
                    if x_prev == 0 and y_prev == 0:
                        x_prev, y_prev = x1, y1
                    else:
                        if is_eraser:
                            cv2.line(drawing_layer, (x_prev, y_prev), (x1, y1), (0, 0, 0), eraser_thickness)
                        else:
                            cv2.line(drawing_layer, (x_prev, y_prev), (x1, y1), draw_color, brush_thickness)
                    x_prev, y_prev = x1, y1

            # Combine drawing with camera feed
            mask = np.where(drawing_layer != 0)
            img[mask] = drawing_layer[mask]

            # Show the image
            cv2.imshow("Air Draw", img)

            # Handle key presses
            key = cv2.waitKey(1)
            if key == ord('q'):  # Quit
                break
            elif key == ord('c'):  # Clear canvas
                drawing_layer = np.zeros((720, 1280, 3), np.uint8)
                print("Canvas cleared")
            elif key == ord('s'):  # Save drawing
                filename = "drawing.jpg"
                # Create a white background for saving
                save_img = np.ones((720, 1280, 3), np.uint8) * 255
                save_img[mask] = drawing_layer[mask]
                cv2.imwrite(filename, save_img)
                print(f"Drawing saved as {filename}")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Closing application...")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 