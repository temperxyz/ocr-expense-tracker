import re
from dateutil.parser import ParserError
from dateutil import parser as date_parser
def extract_total(text):
    lines = text.split("\n")
    candidate_lines = []

    for line in lines:
        cleanline = re.sub(r"(\d)\s+\.", r"\1.", line)
        cleanline = re.sub(r"(\d)\s+(\d{2})\b", r"\1.\2", cleanline)#Fix if misread '.' as ' ' replaces it to catch total
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


def extract_date(text):
    lines = text.split("\n")
    time_pattern = re.compile(r"\d{1,2}:\d{2}\s*(AM|PM)?", re.IGNORECASE)
    fallback = None

    for line in lines:
        match = re.search(
            r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b|\b(\d{1,2}\s+)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b(,?\s+\d{4})\b",
            line, flags=re.IGNORECASE
        )
        if match:
            try:
                parsed = date_parser.parse(match.group(), fuzzy=True)
            except ParserError:
                continue

            if time_pattern.search(line):
                return parsed          # date + time together = high confidence real timestamp
            elif fallback is None:
                fallback = parsed      # keep as backup only

    return fallback

def parse_receipt(text):
    return {
        "merchant": None,  # deliberately out of scope per your risk-management plan
        "date": extract_date(text),
        "total": extract_total(text),
        "raw_text": text,
    }