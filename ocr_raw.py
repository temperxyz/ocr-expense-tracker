import pytesseract 
import re
from preprocess import find_receipt_corners, order_points,warp_receipt,binarize
from PIL import Image
from parser import extract_total,extract_date
import cv2
pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path to where Tesseract is installed on your system
def count_real_words(text):
    tokens=text.split() 
    count=0
    for token in tokens:
        if re.search(r"[a-zA-Z]{3,}",token):
            count+=1
    return count

def get_best_ocr_result(candidates):
    best_score = -1
    best_text = ""

    for candidate_img, psm,label in candidates:
        score=get_confidence_score(candidate_img,psm)
        if score > best_score:
            best_score = score
            best_label=label
            config= f"--psm {psm}"
            text=pytesseract.image_to_string(candidate_img,config=config)
            best_text = text
    return best_text,best_label
def get_confidence_score(img, psm):
    config = f"--psm {psm}"
    data = pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
    confidences = []
    for conf in data['conf']:
        temp=int(conf)
        if temp != -1:
            confidences.append(temp)
    if not confidences:
        return 0  # no valid words found at all
    
    average_confidence = sum(confidences) / len(confidences)
    return average_confidence

img_file=r"samples\mysample_2.jpg"
no_noised= r"temp\no_noise.jpg"
print(get_confidence_score(img_file,6))


img=cv2.imread(img_file) # open in memory
corners=find_receipt_corners(img)
if corners is not None:
    debug_img=img.copy()
    cv2.drawContours(debug_img,[corners],-1,(0,255,0),3)
    cv2.imwrite("contours_debug.jpg",debug_img)
    new_img=warp_receipt(img,corners)
    print(corners)
    cv2.imwrite("warped_debug.jpg", new_img)
    print(new_img.shape)
    candidates=[]
    for label,image in [("Original",img),("Warped",new_img),("Original Binarized",binarize(img)),("Warped Binarized",binarize(new_img))]:
        for psm in [4,6]:
            candidates.append((image,psm,label))

else:
    binarize_img=binarize(img)
    candidates=[]
    for label,image in [("Original",img),("Binarized Original",binarize_img)]:
        for psm in [4,6]:
            candidates.append((image,psm,label))

best_text,best_label=get_best_ocr_result(candidates)
print("The best Image was " + best_label)
print("BEST Text OCR result:",best_text)
total=extract_total(best_text)
if total is None:
    print("Failed to find keyword total")
else:
    print("The receipt total is: ", total)
date=extract_date(best_text)
if date is None:
    print("No date found")
else:
    print("Date found", date)