import sys
import os

# Add parent directory to path so we can import ocr_processor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ocr_processor import ocr_processor

def create_dummy_image_with_text(text, filename="test_ocr_image.jpg"):
    import cv2
    import numpy as np
    
    # Create a white image
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "Patient ID:", (50, 100), font, 1, (0, 0, 0), 2)
    cv2.putText(img, text, (50, 150), font, 1.2, (0, 0, 0), 3)
    
    cv2.imwrite(filename, img)
    return filename

def test_ocr():
    test_id = "12345678"
    filename = create_dummy_image_with_text(test_id)
    
    print(f"Created test image {filename} with ID {test_id}")
    
    extracted_id = ocr_processor.extract_patient_id(filename)
    
    if extracted_id == test_id:
        print("SUCCESS: OCR correctly extracted the ID.")
    else:
        print(f"FAILURE: OCR extracted '{extracted_id}', expected '{test_id}'")
        
    # Clean up
    if os.path.exists(filename):
        os.remove(filename)

    input("Press Enter to close this window...")

if __name__ == "__main__":
    test_ocr()
