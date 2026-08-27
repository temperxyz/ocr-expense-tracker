import pytesseract
import re
import cv2
from preprocess import find_receipt_corners, order_points, warp_receipt, adaptive_binarize, resize_for_ocr

pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def count_real_words(text):
    tokens=text.split()
    count=0
    for token in tokens:
        if re.search(r"[a-zA-Z]{3,}", token):
            count+=1
    return count

def get_confidence_score(img, psm):
    config=f"--psm {psm}"
    data=pytesseract.image_to_data(img, config=config, output_type=pytesseract.Output.DICT)
    confidences=[float(c) for c in data['conf'] if float(c)>=0]
    if not confidences:
        return 0
    text=" ".join(data['text'])
    receipt_words=len(re.findall(r"\b(total|subtotal|tax|date|cash|change|balance|amount|paid)\b",text,flags=re.IGNORECASE))#confidence alone can prefer meaningless text so reward receipt words too
    return sum(confidences) / len(confidences)+receipt_words*3

def get_best_ocr_result(candidates):
    best_score=-1
    best_text=""
    best_label=""
    best_candidate=None
    for candidate_img, psm, label in candidates:
        score=get_confidence_score(candidate_img, psm)
        if score>best_score:
            best_score=score
            best_label=label
            best_candidate=(candidate_img,psm)
    if best_candidate is not None:
        candidate_img,psm=best_candidate
        config=f"--psm {psm}"
        best_text=pytesseract.image_to_string(candidate_img, config=config)
    return best_text, best_label

def extract_text_from_receipt(image_path):
    """Takes an image path, returns (raw_text, best_label) — the Phase 6 entry point."""
    img=cv2.imread(image_path)
    img=resize_for_ocr(img)#keeps OCR time reasonable for large phone photos
    corners=find_receipt_corners(img)

    if corners is not None:
        new_img=warp_receipt(img, corners)
        candidates=[]
        for label, image in [("Original", img), ("Warped", new_img),
                              ("Original Adaptive", adaptive_binarize(img)),
                              ("Warped Adaptive", adaptive_binarize(new_img))]:
            for psm in [6, 11]:
                candidates.append((image, psm, label))
    else:
        adaptive_img=adaptive_binarize(img)
        candidates=[]
        for label, image in [("Original", img), ("Adaptive Original", adaptive_img)]:
            for psm in [6, 11]:
                candidates.append((image, psm, label))

    best_text, best_label=get_best_ocr_result(candidates)
    return best_text, best_label

if __name__ == "__main__":
    text, label=extract_text_from_receipt(r"samples\image1.jpg")
    print("Best image was:", label)
    print("Best OCR text:", text)
