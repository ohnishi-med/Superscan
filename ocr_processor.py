import easyocr
import cv2
import re
import os
import numpy as np

# Suppress minimal logging from EasyOCR/PyTorch if desired
# os.environ["EASYOCR_MODULE_LOADING"] = "0"

class OCRProcessor:
    def __init__(self):
        print("Initializing EasyOCR (this may take a moment)...")
        # Initialize for Japanese and English
        # gpu=True if CUDA is available, else False. EasyOCR handles this automatically usually, 
        # but explicit False is safer for non-CUDA envs unless checked.
        # Allowing GPU if available for speed.
        self.reader = easyocr.Reader(['en'], gpu=True) 
        print("EasyOCR Initialized.")

    def extract_patient_id(self, image_path):
        """
        Reads image from image_path and extracts the patient ID.
        Returns ID string or None.
        """
        try:
            print(f"OCR: Processing {image_path}...")
            
            # 1. Read Image
            # EasyOCR supports file path directly
            result = self.reader.readtext(image_path)
            
            # result format: [(bbox, text, prob), ...]
            print(f"OCR Raw Result: {result}")
            
            candidates = []
            
            # 2. Extract Candidates using Regex
            # Looking for 8-10 digit numbers
            # Sometimes OCR reads 'I' or 'l' as '1', 'O' as '0', but EasyOCR is decent.
            # We strictly look for digits for now.
            id_pattern = re.compile(r'\d{8,10}')
            
            for (bbox, text, prob) in result:
                # Basic cleaning
                clean_text = text.replace(' ', '').replace('-', '')
                
                # Check match
                match = id_pattern.search(clean_text)
                if match:
                    candidates.append({
                        "id": match.group(),
                        "prob": prob,
                        "text": text
                    })
            
            if not candidates:
                print("OCR: No ID pattern found.")
                return None
            
            # 3. Select Best Candidate
            # Logic: Highest probability
            candidates.sort(key=lambda x: x["prob"], reverse=True)
            
            best_id = candidates[0]['id']
            print(f"OCR: Found ID {best_id} (prob: {candidates[0]['prob']:.2f})")
            return best_id

        except Exception as e:
            print(f"OCR Error: {e}")
            return None

# Global instance
ocr_processor = OCRProcessor()
