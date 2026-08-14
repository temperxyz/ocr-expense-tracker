from transformers import pipeline

# Load once at module level — NOT inside the function.
# Why? Think about what happens if this line were inside categorize_expense()
# and you called it 50 times processing 50 receipts...
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

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

    # groceries
    "carrefour": "groceries",
    "imtiaz": "groceries",
    "al fatah": "groceries",
    "metro cash": "groceries",
    "hyperstar": "groceries",

    # food & dining
    "cheezious": "food & dining",
    "kfc": "food & dining",
    "mcdonald": "food & dining",
    "dominos": "food & dining",
    "foodpanda": "food & dining",
    "cafe": "food & dining",
    "restaurant": "food & dining",
    "ranchers": "food & dining",

    # utilities
    "electric": "utilities",
    "wapda": "utilities",
    "gas": "utilities",
    "ptcl": "utilities",
    "internet": "utilities",
    "water":"utilities",

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

    # shopping
    "outfitters": "shopping",
    "khaadi": "shopping",
    "daraz": "shopping",
    "mall": "shopping",
    "olx":"shopping",
    "j.":"shopping",
    "ideas":"shopping",
    "amazon":"shopping"
}

def categorize_expense(merchant_text):
    """
    Takes a merchant name (string), returns (category, confidence).
    """
    lowercase=merchant_text.lower()
    if not lowercase:
        return "other", 0.0  # no text to work with, don't even call the model
    for keyword,category in KEYWORD_OVERRIDES.items():
        if keyword in lowercase:
            return category,1.0

    result=classifier(lowercase,candidate_labels=CATEGORIES)
    toplabel=result["labels"][0]# return category name
    topscore=result["scores"][0]# return the score
    return toplabel,topscore
    pass


if __name__ == "__main__":
    test_merchants = ["Whole Foods Market", "Uber", "Cheezious", "Shell Gas Station"]
    for m in test_merchants:
        print(m, "->", categorize_expense(m))   