import pytesseract
import re
import cv2
from preprocess import find_receipt_corners, order_points, warp_receipt, binarize

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
    confidences=[int(c) for c in data['conf'] if int(c)!=-1]
    if not confidences:
        return 0
    return sum(confidences) / len(confidences)

def get_best_ocr_result(candidates):
    best_score=-1
    best_text=""
    best_label=""
    for candidate_img, psm, label in candidates:
        score=get_confidence_score(candidate_img, psm)
        if score>best_score:
            best_score=score
            best_label=label
            config=f"--psm {psm}"
            best_text=pytesseract.image_to_string(candidate_img, config=config)
    return best_text, best_label

def extract_text_from_receipt(image_path):
    """Takes an image path, returns (raw_text, best_label) — the Phase 6 entry point."""
    img=cv2.imread(image_path)
    corners=find_receipt_corners(img)

    if corners is not None:
        new_img=warp_receipt(img, corners)
        candidates=[]
        for label, image in [("Original", img), ("Warped", new_img),
                              ("Original Binarized", binarize(img)),
                              ("Warped Binarized", binarize(new_img))]:
            for psm in [4, 6]:
                candidates.append((image, psm, label))
    else:
        binarize_img=binarize(img)
        candidates=[]
        for label, image in [("Original", img), ("Binarized Original", binarize_img)]:
            for psm in [4, 6]:
                candidates.append((image, psm, label))

    best_text, best_label=get_best_ocr_result(candidates)
    return best_text, best_label

if __name__ == "__main__":
    text, label=extract_text_from_receipt(r"samples\image1.jpg")
    print("Best image was:", label)
    print("Best OCR text:", text)