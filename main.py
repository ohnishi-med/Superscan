import threading
import uvicorn
import pystray
from PIL import Image, ImageDraw
import sys
import os
from server import app
from camera_manager import camera_manager
from cv2_enumerate_cameras import enumerate_cameras
import functools

# Flag to control server loop
should_exit = False

def create_image(width=64, height=64, color1="blue", color2="white"):
    """
    Generates a simple icon image if scan_icon.png is missing.
    """
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def load_icon():
    icon_path = "icon.png"
    if os.path.exists(icon_path):
        return Image.open(icon_path)
    else:
        # Fallback: Create a dummy icon
        return create_image()

def run_server():
    """
    Runs the Uvicorn server in a separate thread.
    """
    # log_config=None suppresses default Uvicorn logs to console if needed
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=None)

def on_exit(icon, item):
    """
    Handles Clean Exit.
    """
    global should_exit
    should_exit = True
    icon.stop()
    # Force exit since Uvicorn thread is daemon but sometimes lingers
    os._exit(0) 

def setup_tray():
    icon_image = load_icon()
    
    # 1. Get Cameras
    camera_items = []
    try:
        cameras = list(enumerate_cameras())
        for cam in cameras:
            def on_camera_select(icon, item, camera_index=cam.index):
                print(f"Switching to Camera: {camera_index}")
                camera_manager.restart_camera(camera_index)
            
            # Simple check mark logic could be added here if we track state in icon.user_data
            camera_items.append(pystray.MenuItem(f"{cam.name}", on_camera_select))
    except Exception as e:
        print(f"Camera enumeration failed: {e}")
        camera_items.append(pystray.MenuItem("Error listing cameras", None, enabled=False))

    # Fallback if empty (No devices found)
    if not camera_items:
        camera_items.append(pystray.MenuItem("No physical cameras", None, enabled=False))

    # Define menu items
    menu = pystray.Menu(
        pystray.MenuItem("Superscan: Active", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Cameras", pystray.Menu(*camera_items)),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit)
    )

    icon = pystray.Icon("Superscan", icon_image, "Superscan", menu)
    
    # Start Camera Manager in active mode detection
    camera_manager.start()

    # Start Server in Background Thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    try:
        # Run Tray App (Blocking Main Thread)
        icon.run()
    finally:
        camera_manager.stop()

if __name__ == "__main__":
    setup_tray()
