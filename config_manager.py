import os
import dotenv
from pathlib import Path

class ConfigManager:
    def __init__(self, env_path=".env"):
        self.env_path = Path(env_path)
        if not self.env_path.exists():
            # Create empty .env if not exists
            self.env_path.touch()
        
        dotenv.load_dotenv(self.env_path, override=True)

    def get(self, key, default=None):
        """Get setting from environment variables."""
        # Reload to ensure we have latest from file if changed externally
        dotenv.load_dotenv(self.env_path, override=True)
        return os.getenv(key, default)

    def set(self, key, value):
        """Set setting and save to .env file."""
        dotenv.set_key(str(self.env_path), key, str(value))
        # Ensure os.environ is updated for the current process
        os.environ[key] = str(value)

    def get_all(self):
        """Get all relevant settings as a dict."""
        dotenv.load_dotenv(self.env_path, override=True)
        return {
            "CAMERA_INDEX": int(os.getenv("CAMERA_INDEX", 0)),
            "MIN_AREA_THRESHOLD": int(os.getenv("MIN_AREA_THRESHOLD", 5000)),
            "MOTION_WAIT_TIME": float(os.getenv("MOTION_WAIT_TIME", 1.5)),
            "ECO_MODE_DELAY": float(os.getenv("ECO_MODE_DELAY", 10.0)),
            "TEMP_DIR": os.getenv("TEMP_DIR", "temp"),
            "OCR_ENGINE": os.getenv("OCR_ENGINE", "EasyOCR"),
            "TESSERACT_PATH": os.getenv("TESSERACT_PATH", "")
        }

# Global instance
config_manager = ConfigManager()
