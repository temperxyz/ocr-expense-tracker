import re
from dateutil.parser import ParserError
from dateutil import parser as date_parser
TOTAL_LABELS=re.compile(r"\b(grand\s*total|total\s*due|amount\s*due|net\s*total|balance|bal|total|paid)\b",flags=re.IGNORECASE)#different vendors use different names for the final amount
def get_total_lines(lines):
    #sorts total-ish lines into 3 buckets, grand total is best, plain total is
    #fine, but subtotal/tax lines are last resort only cause those arent the
    #actual total we want
    grand=[]
    normal=[]
    taxsub=[]
    for i,line in enumerate(lines):
        cleanline = re.sub(r"(\d)\s+\.", r"\1.", line)
        cleanline = re.sub(r"(\d)\s+(\d{2})\b", r"\1.\2", cleanline)#Fix if misread '.' as ' '
        if TOTAL_LABELS.search(cleanline) and not re.search(r"\d",cleanline):
            for nextline in lines[i+1:i+4]:
                nextline=nextline.strip()
                if nextline and re.search(r"\d",nextline):
                    cleanline += " "+nextline#some receipts print TOTAL and its amount on a nearby line
                    break
        if not TOTAL_LABELS.search(cleanline):
            continue
        if re.search(r"grand\s*total|total\s*due|amount\s*due|net\s*total",cleanline,flags=re.IGNORECASE):
            grand.append(cleanline)
        elif re.search(r"subtotal|sub\s*total|\btax\b|\bchange\b|\bcash\b|\btend\b",cleanline,flags=re.IGNORECASE):
            taxsub.append(cleanline)
        else:
            normal.append(cleanline)
    return grand,normal,taxsub

def pick_amount(line):
    #if theres a currency symbol grab the number right after it, thats usually
    #the actual amount and not some random quantity on the line (like "14" in
    #"total for 14 item is $32"). if no symbol just take the last number since
    #the amount is usually at the end of the line
    currency_match=re.search(r"(?:rs\.?|pkr|\$)\s*([\d,]+(?:\.\d{1,2})?)",line,flags=re.IGNORECASE)
    if currency_match:
        num=currency_match.group(1)
    else:
        all_nums=re.findall(r"[\d,]+(?:\.\d{1,2})?",line)
        if not all_nums:
            return None
        num=all_nums[-1]
    clean_num=re.sub(r"[,]","",num)
    try:
        return float(clean_num)
    except ValueError:
        return None

def extract_total(text):
    lines = text.split("\n")
    grand,normal,taxsub=get_total_lines(lines)
    for bucket in (grand,normal,taxsub):#try grand total first, then normal, only fall to tax/subtotal if nothing else
        if bucket:
            chosen_line=bucket[-1]
            amount=pick_amount(chosen_line)
            if amount is not None:
                return amount
    return None #Fails check


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
    if fallback is not None:
        return fallback
    #regex didnt catch anything, probably ocr messed up the slashes/dots (like reading
    #10/O5/2026 with a letter O). try swapping the common misreads and just throw it
    #at dateutil directly instead of matching our own pattern
    for line in lines:
        cleaned=line.replace("O","0").replace("o","0")
        if not re.search(r"\d",cleaned):
            continue
        try:
            parsed=date_parser.parse(cleaned,fuzzy=True)
            return parsed
        except (ParserError,ValueError,OverflowError):
            continue
    return fallback

def parse_receipt(text):
    return {
        "merchant": None,  # deliberately out of scope per your risk-management plan
        "date": extract_date(text),
        "total": extract_total(text),
        "raw_text": text,
    }
