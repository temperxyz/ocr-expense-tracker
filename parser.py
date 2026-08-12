import re
from dateutil.parser import ParserError

def extract_total(text):
    lines = text.split("\n")
    candidate_lines = []

    for line in lines:
        cleanline = re.sub(r"(\d)\s+\.", r"\1.", line)
        keyword_match = re.search(r"\btotal\b", cleanline, flags=re.IGNORECASE)
        number_match = re.search(r"[\d,]+\.\d{2}", cleanline)

        if keyword_match and number_match:#Both number and line is present
            if keyword_match.start() < number_match.start():# meaning total appear before the amount
                candidate_lines.append(cleanline)
            pass
    if not candidate_lines:
        return None #Fails check
    chosen_line=""
    wordtofind=r"\b"+"Grand Total" +r"\b"# idk but i think this can have a problem like what if its Grand Total: or GrandTotal these variations could make it difficult
    for items in candidate_lines:
        if re.search(wordtofind,items,flags=re.IGNORECASE):
            chosen_line=items
        pass
    if chosen_line=="":#Meaning Grandtotal wasnt there so mostly the last total is the actual total
        chosen_line=candidate_lines[-1]
   
    floatnum=re.search(r"[\d,]+\.\d{2}",chosen_line)
    if floatnum is None:
        return None
    clean_num=re.sub(r"[,]","",floatnum.group())
    result=float(clean_num)

    return result  # replace with your parsed float
from dateutil import parser as date_parser
from dateutil.parser import ParserError

def extract_date(text):
    """
    Takes raw OCR text, returns the best-guess date as a string
    (normalized format), or None if nothing confident was found.
    """
    lines = text.split("\n")

    for line in lines:
        match=re.search(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b|\b(\d{1,2}\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b(,?\s+\d{4})?\b",line,flags=re.IGNORECASE)# Checking if the line contains a digit
        if match:
            try:
                parsed=date_parser.parse(match.group(),fuzzy=True)# ignores the surrounding text and focus on thedate part only
                return parsed
            except ParserError:
                print("The Text couldnt be parsed as a date")
        pass
    return None

def parse_receipt(text):
    """
    Main entry point for Phase 3. Takes raw OCR text (best_text from
    ocr_raw.py), returns a structured dict.
    """
    return {
        "merchant": None,  # deliberately out of scope per your risk-management plan
        "date": extract_date(text),
        "total": extract_total(text),
        "raw_text": text,
    }


if __name__ == "__main__":
    # TODO: paste in one of your actual best_text outputs here as a string
    # (e.g. the Trader Joe's one) and run this file directly to test
    # extract_total and extract_date in isolation, without needing to
    # re-run OCR every time. This is your quick iteration loop for Phase 3.
    sample_text = """
    PASTE A REAL OCR OUTPUT HERE
    """
    floatnum = re.search(r"[\d,]+\.\d{2}", "TOTAL 23.19")
    print(floatnum)          # what you showed above - a Match object
    print(floatnum.group())  # what does THIS print?
    #print(parse_receipt(sample_text))