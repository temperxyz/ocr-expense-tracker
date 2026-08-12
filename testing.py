from dateutil import parser as date_parser
from dateutil.parser import ParserError

test_lines = [
    "06-28-2014 12:34PM 0403 04 1346 4683",   # Trader Joe's - real date
    "R-CARROTS SHREDDED 10 OZ",                 # Trader Joe's - noise
    "EGGS 1 002 ORGANIC BROWN.",                # Trader Joe's - noise
    "99/08/14",                                  # Winco - real date, unusual format
    "3ANANAS LOOSE 17KG",                       # SPAR - noise
    "0,596kg @ —15.99R /kg 9.53 *",             # SPAR - noise, has decimals
]

for line in test_lines:
    try:
        result = date_parser.parse(line, fuzzy=True)
        print(f"{line!r} -> PARSED AS: {result}")
    except Exception as e:
        print(f"{line!r} -> FAILED: {type(e).__name__}: {e}")