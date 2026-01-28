import cv2
import time
import os
import threading
from datetime import datetime
import uuid
from config_manager import config_manager

class CameraManager:
    def __init__(self):
        self.camera_index = int(config_manager.get("CAMERA_INDEX", 0))
        self.min_area = int(config_manager.get("MIN_AREA_THRESHOLD", 5000))
        self.motion_wait = float(config_manager.get("MOTION_WAIT_TIME", 1.5))
        self.eco_delay = float(config_manager.get("ECO_MODE_DELAY", 10.0))
        self.temp_dir = config_manager.get("TEMP_DIR", "./temp")
        
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        self.cap = None
        self.is_running = False
        self.is_eco_mode = True
        self.last_motion_time = time.time()
        self.motion_start_time = None
        self.is_stabilized = False
        self.last_capture_time = 0
        
        # Background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)
        
        self.thread = None
        self.latest_frame = None
        self.new_scan_event = None # To be used to notify API

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def restart_camera(self, new_index):
        """
        Stops the current camera and starts a new one with the given index.
        """
        print(f"Restarting camera with index: {new_index}")
        self.stop()
        # Wait a bit for thread to clean up if needed, though stop() sets is_running=False
        #Ideally we join the thread but for simplicity:
        time.sleep(1.0)
        
        self.camera_index = int(new_index)
        self.start()

    def _run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Check if camera opened, if not, enter Mock Mode
        if not self.cap.isOpened():
            print(f"Warning: Camera {self.camera_index} not found. Running in MOCK MODE.")
        
        while self.is_running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
            else:
                # MOCK MODE: Generate a random frame with a moving circle
                frame = self._generate_mock_frame()
            
            self.latest_frame = frame.copy()
            
            # 1. Motion Detection
            has_motion = self._detect_motion(frame)
            current_time = time.time()

            if has_motion:
                self.last_motion_time = current_time
                if self.is_eco_mode:
                    print("Motion detected! Switching to ACTIVE mode.")
                    self.is_eco_mode = False
                
                # Reset stabilization wait if moving
                self.motion_start_time = current_time
                self.is_stabilized = False
            else:
                # 2. Eco Mode Transition
                if not self.is_eco_mode and (current_time - self.last_motion_time > self.eco_delay):
                    print("No motion. Entering ECO mode.")
                    self.is_eco_mode = True

                # 3. Stabilization & Capture Logic
                if not self.is_eco_mode and not self.is_stabilized:
                    # If we had motion before, and now it's still for enough time
                    if current_time - self.last_motion_time >= self.motion_wait:
                        self.is_stabilized = True
                        self._capture_image(frame)

            # 4. FPS Control (Eco vs Active)
            if self.is_eco_mode:
                time.sleep(0.5) # ~2 FPS
            else:
                time.sleep(0.03) # ~30 FPS

    def _generate_mock_frame(self):
        """Generates a dummy frame with a moving object for testing motion detection."""
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a moving "document" (white rectangle)
        t = time.time()
        # Move document every 15 seconds to simulate someone placing it
        cycle = int(t / 15) % 2
        if cycle == 1:
            # Simulate a document being placed and held still
            cv2.rectangle(frame, (100, 100), (540, 380), (255, 255, 255), -1)
            cv2.putText(frame, f"Mock Document (Still) - ID: 123456", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        else:
            # Simulate an empty background
            cv2.putText(frame, "Empty Background (Waiting...)", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
        return frame

    def _detect_motion(self, frame):
        # Resize for faster processing
        small_frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        fg_mask = self.bg_subtractor.apply(gray)
        
        # Count white pixels in mask
        motion_area = cv2.countNonZero(fg_mask)
        return motion_area > self.min_area

    def _capture_image(self, frame):
        # Avoid duplicate captures within 2 seconds
        if time.time() - self.last_capture_time < 2.0:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"scan_{timestamp}_{unique_id}.jpg"
        filepath = os.path.join(self.temp_dir, filename)
        
        cv2.imwrite(filepath, frame)
        self.last_capture_time = time.time()
        print(f"Captured: {filename}")
        
        # Here we would normally trigger the AI analysis
        # For now, we just save it.
        
    def get_latest_frame_encoded(self):
        """Returns the latest frame as a base64 string for preview if needed."""
        if self.latest_frame is None:
            return None
        _, buffer = cv2.imencode('.jpg', self.latest_frame)
        return buffer

camera_manager = CameraManager()
