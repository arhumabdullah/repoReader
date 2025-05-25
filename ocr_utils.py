import cv2
import pytesseract
import re
from PIL import Image
import numpy as np

# Set path for tesseract if needed
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Define a dictionary with CBC tests and their normal ranges
tests_info = {
    "hemoglobin": "13-17",         # g/dL
    "hematocrit": "38-50",         # %
    "wbc": "4.5-11.0",             # x10^9/L
    "rbc": "4.5-5.9",              # x10^12/L
    "platelets": "150-450",        # x10^9/L
    "mcv": "80-100",               # fL
    "mch": "27-33",                # pg
    "mchc": "320-360",             # g/L
    "neutrophils": "40-60",        # %
    "lymphocytes": "20-40",        # %
    "monocytes": "2-8",            # %
    "eosinophils": "1-4",          # %
    "basophils": "0-1",            # %
}

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy:
    - Convert to grayscale
    - Apply Gaussian blur
    - Apply Otsu's thresholding
    """
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshed = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshed

def extract_text_from_image(image):
    """
    Extract text from processed image using pytesseract OCR
    """
    return pytesseract.image_to_string(image)

def parse_test_data(text):
    """
    Parse the OCR extracted text to structured data (test names, values, ranges, and units).
    Dynamically detect CBC tests from the text.
    """
    lines = text.split("\n")
    structured_data = []

    for line in lines:
        line_lower = line.lower()
        
        for test_name, normal_range in tests_info.items():
            # Use regular expressions to detect test names in the line
            if re.search(rf"\b{test_name}\b", line_lower):  # Match test name, case insensitive
                parts = line.split()
                
                try:
                    # Extract the value (float) from the line
                    value = None
                    for part in parts:
                        try:
                            value = float(part)
                            break
                        except:
                            continue
                    if value is None:
                        continue  # Skip if no numerical value is found

                    # Extract the unit (if present)
                    unit = ""
                    for part in parts:
                        if any(u in part.lower() for u in ["mg/dl", "g/dl", "mmol/l", "x10^9/l", "fL", "pg", "%"]):
                            unit = part
                            break

                    structured_data.append({
                        "test": test_name.capitalize(),
                        "value": value,
                        "range": normal_range,
                        "unit": unit
                    })
                except Exception:
                    continue  # Skip if any error occurs during extraction

    return structured_data
