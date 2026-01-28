from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import glob
from cv2_enumerate_cameras import enumerate_cameras
from ocr_processor import ocr_processor
from config_manager import config_manager
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# Allow CORS for Chrome Extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve scanned files
TEMP_DIR = config_manager.get("TEMP_DIR", "./temp")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
app.mount("/files", StaticFiles(directory=TEMP_DIR), name="scanned_files")
app.mount("/test", StaticFiles(directory="test"), name="test_files")

# Simple in-memory tracker for processed files and results
processed_files = set()
scan_results = {} # filename -> {"patient_id": "...", "checked": bool}

@app.get("/status")
def get_status():
    return {"status": "running", "service": "Superscan Backend"}

@app.get("/cameras")
def get_cameras():
    """
    Returns a list of available camera devices.
    Uses cv2_enumerate_cameras for Windows-friendly names.
    """
    try:
        cameras = []
        for cam in enumerate_cameras():
             cameras.append({
                "index": cam.index,
                "name": cam.name,
                "path": cam.path
            })
        return {"cameras": cameras}
    except Exception as e:
        return {"error": str(e), "cameras": []}

class SettingsUpdate(BaseModel):
    settings: Dict[str, Any]

@app.get("/settings")
async def get_settings():
    """Returns the current application settings."""
    return config_manager.get_all()

@app.post("/settings")
async def update_settings(update: SettingsUpdate):
    """Updates the application settings."""
    for key, value in update.settings.items():
        config_manager.set(key, value)
    return {"status": "success", "updated": update.settings}

@app.get("/check_new_scan")
def check_new_scan():
    """
    Checks if there's a new file in TEMP_DIR that hasn't been processed.
    """
    files = glob.glob(os.path.join(TEMP_DIR, "*.jpg"))
    # Sort by time to get the newest
    files.sort(key=os.path.getmtime, reverse=True)
    
    for f in files:
        filename = os.path.basename(f)
        if filename not in processed_files:
            # Check if we already have AI result
            if filename not in scan_results:
                print(f"Triggering OCR for {filename}...")
                patient_id = ocr_processor.extract_patient_id(f)
                scan_results[filename] = {"patient_id": patient_id}
            
            result = scan_results[filename]
            return {
                "new_file": True,
                "patient_id": result["patient_id"],
                "file_url": f"http://127.0.0.1:8000/files/{filename}",
                "filename": filename
            }
    
    return {"new_file": False}

@app.post("/mark_processed")
def mark_processed(data: dict):
    filename = data.get("filename")
    if filename:
        processed_files.add(filename)
        return {"success": True}
    return {"error": "No filename provided"}

# For direct testing (python server.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
