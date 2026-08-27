from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
"""
Takes a merchant name (string), returns (status, category, confidence).
status is one of: "confident" (keyword match), "likely" (model, score>=0.5),
"uncertain" (model, score<0.5, or empty input).
"""
CATEGORIES = [
    "groceries",
    "food & dining",
    "transport",
    "utilities",
    "shopping",
    "entertainment",
    "other",
]

# Hardcoded overrides for cases the model will predictably botch.
# Keys should be lowercase substrings to check against the merchant name.
KEYWORD_OVERRIDES = {
    # transport
    "uber": "transport",
    "careem": "transport",
    "indrive": "transport",
    "yango": "transport",
    "railway": "transport",
    "airline": "transport",
    "petrol": "transport",
    "shell": "transport",
    "total parco": "transport",
    "pso": "transport",
    "transport":"transport",

    # groceries
    "carrefour": "groceries",
    "imtiaz": "groceries",
    "al fatah": "groceries",
    "metro cash": "groceries",
    "hyperstar": "groceries",
    "groceries": "groceries",
    " mart ": "groceries",

    # food & dining
    "cheezious": "food & dining",
    "kfc": "food & dining",
    "mcdonald": "food & dining",
    "dominos": "food & dining",
    "foodpanda": "food & dining",
    "cafe": "food & dining",
    "restaurant": "food & dining",
    "ranchers": "food & dining",
    "food": "food & dining",

    # utilities
    "electric": "utilities",
    "wapda": "utilities",
    "gas": "utilities",
    "ptcl": "utilities",
    "internet": "utilities",
    "water":"utilities",
    "utility":"utilities",

      # entertainment
    "netflix": "entertainment",
    "cinepax": "entertainment",
    "nueplex": "entertainment",
    "cinema": "entertainment",
    "imax": "entertainment",
    "spotify": "entertainment",
    "youtube premium": "entertainment",
    "steam": "entertainment",
    "playstation": "entertainment",
    "gaming": "entertainment",
    "entertainment": "entertainment",

    # shopping
    "outfitters": "shopping",
    "khaadi": "shopping",
    "daraz": "shopping",
    "mall": "shopping",
    "olx":"shopping",
    "j.":"shopping",
    "ideas":"shopping",
    "amazon":"shopping",
    "shopping": "shopping"
    ,"shop":"shopping"
}

def categorize_expense(merchant_text):
    """
    Takes a merchant name (string), returns (category, confidence).
    """
    
    if not merchant_text:
        return "uncertain","other", 0.0  # no text to work with, don't even call the model
    lowercase=merchant_text.lower()
    for keyword,category in KEYWORD_OVERRIDES.items():
        if keyword in lowercase:
            return "confident",category,1.0

    result=classifier(lowercase,candidate_labels=CATEGORIES)
    toplabel=result["labels"][0]# return top category name
    topscore=result["scores"][0]# return the score
    if topscore<0.5:
        return "uncertain",toplabel,topscore
    return "likely",toplabel,topscore


if __name__ == "__main__":
    test_merchants = [
        # clean, no keyword hit — model has to work unassisted
        "Bata",
        "Chase Value",
        "Al-Fatah Super Store",   # typo'd version, won't match "al fatah" dict key

        # ambiguous / edge cases
        "Total",
        "Al Meezan Bank",
        "J.",                    

        # garbled, OCR-style noise — the realistic test
        "UBEER",
        "CARREFDUR",
        "CHEEZI0US",
        "5HELL",
        "WH0LE F00D5 MARKET",
        "",                       
        None,                     
    ]
    for m in test_merchants:
        print(m, "->", categorize_expense(m))
