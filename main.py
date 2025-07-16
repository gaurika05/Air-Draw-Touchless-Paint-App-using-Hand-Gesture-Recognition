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

class AirDraw:
    def __init__(self):
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)  # width
        self.cap.set(4, 720)   # height

        # Initialize hand detector
        self.detector = HandDetector(detection_confidence=0.85)

        # Drawing variables
        self.draw_color = (255, 0, 0)  # Default blue
        self.brush_thickness = 15
        self.eraser_thickness = 50
        self.is_eraser = False
        
        # Create drawing layer (transparent)
        self.drawing_layer = np.zeros((720, 1280, 3), np.uint8)
        
        # Previous coordinates for drawing
        self.x_prev = 0
        self.y_prev = 0
        
        # Color options (removed black)
        self.colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (0, 255, 255),  # Yellow
            (255, 255, 255) # Eraser
        ]
        
        # Color selection boxes
        self.color_boxes = []
        for i, color in enumerate(self.colors):
            self.color_boxes.append([int(1280/6 * (i+1)), 0, int(1280/6 * (i+1) + 50), 50, color])

    def get_frame(self):
        success, img = self.cap.read()
        if not success:
            return None
            
        img = cv2.flip(img, 1)  # Mirror image

        # Find hand landmarks
        img = self.detector.find_hands(img)
        landmark_list = self.detector.find_position(img)

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
                for x, y, w, h, color in self.color_boxes:
                    if x < x1 < w and y < y1 < h:
                        if color == (255, 255, 255):  # Eraser
                            self.is_eraser = True
                            self.draw_color = color
                            self.brush_thickness = self.eraser_thickness
                        else:
                            self.is_eraser = False
                            self.draw_color = color
                            self.brush_thickness = 15
                
                # Draw selection boxes
                for x, y, w, h, color in self.color_boxes:
                    cv2.rectangle(img, (x, y), (w, h), color, cv2.FILLED)
                    # Add black border to white eraser box for visibility
                    if color == (255, 255, 255):
                        cv2.rectangle(img, (x, y), (w, h), (0, 0, 0), 2)
                    if color == self.draw_color:
                        cv2.rectangle(img, (x, y), (w, h), (128, 128, 128), 3)

                self.x_prev, self.y_prev = 0, 0  # Reset previous points

            # Drawing Mode - Index finger up
            elif len(fingers) == 1:
                if self.x_prev == 0 and self.y_prev == 0:
                    self.x_prev, self.y_prev = x1, y1
                else:
                    if self.is_eraser:
                        cv2.line(self.drawing_layer, (self.x_prev, self.y_prev), (x1, y1), (0, 0, 0), self.eraser_thickness)
                    else:
                        cv2.line(self.drawing_layer, (self.x_prev, self.y_prev), (x1, y1), self.draw_color, self.brush_thickness)
                self.x_prev, self.y_prev = x1, y1

        # Combine drawing with camera feed
        mask = np.where(self.drawing_layer != 0)
        img[mask] = self.drawing_layer[mask]

        return img

    def clear_canvas(self):
        self.drawing_layer = np.zeros((720, 1280, 3), np.uint8)

    def save_drawing(self, filename="drawing.jpg"):
        # Create a white background for saving
        save_img = np.ones((720, 1280, 3), np.uint8) * 255
        mask = np.where(self.drawing_layer != 0)
        save_img[mask] = self.drawing_layer[mask]
        cv2.imwrite(filename, save_img)

    def release(self):
        self.cap.release()

    def cleanup(self):
        """Cleanup resources"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

def initialize_air_draw():
    return AirDraw()

if __name__ == "__main__":
    air_draw = AirDraw()
    while True:
        frame = air_draw.get_frame()
        if frame is not None:
            cv2.imshow("Air Draw", frame)
            
            key = cv2.waitKey(1)
            if key == ord('q'):  # Quit
                break
            elif key == ord('c'):  # Clear canvas
                air_draw.clear_canvas()
            elif key == ord('s'):  # Save drawing
                air_draw.save_drawing()
    
    air_draw.cleanup() 