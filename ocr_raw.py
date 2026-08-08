import pytesseract 
from PIL import Image
pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path to where Tesseract is installed on your system
print("Tesseract Version:", pytesseract.get_tesseract_version())