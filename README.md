# OCR Expense Tracker

Final Year Project. You upload a photo of a receipt, the app reads the text off it using OCR, pulls out the date/total/category, and saves it so you can see your spending on a dashboard. Nobody actually logs expenses manually so the goal was to make it as close to "just take a photo" as possible.

## How it works

1. Upload a receipt image
2. OpenCV cleans it up (finds corners, straightens it, converts to black and white etc)
3. Tesseract OCR reads the text
4. Regex + dateutil pulls out date and total from the messy OCR output
5. A pretrained zero-shot model guesses the category from the merchant name
6. You check/fix the fields before saving since OCR is never 100% accurate
7. Saves to SQLite
8. Dashboard tab shows spending by category and over time

## Tech stack

Python, OpenCV, Tesseract (pytesseract), regex + dateutil, HuggingFace transformers (facebook/bart-large-mnli), SQLite, Streamlit, Plotly.

## Why these choices

Used a pretrained model for categorization instead of training my own since I don't have labeled data and there wasn't time to build one. Zero shot classification works without training, just give it category names. It's not perfect on every merchant so I added a keyword override list on top (like "uber" always maps to transport instead of asking the model), so it's a mix of ML and rule based logic, not pure ML.

SQLite instead of MySQL because I didn't want to set up a database server for this, SQLite is just a file.

## How to run it

1. Clone the repo, make a venv and activate it
2. Install Tesseract itself on your machine (separate from the pip package). Windows: get it from the tesseract github. Mac/Linux: `brew install tesseract` or `apt install tesseract-ocr`
3. `pip install -r requirements.txt`
4. On windows you might need to update the tesseract path in ocr_raw.py. Mac/linux usually just works if tesseract is on PATH
5. `streamlit run app.py`

## Known limitations

- Merchant name is manual entry, not auto extracted. The merchant name area gets misread by OCR a lot (logos, weird fonts) so I'd rather the user type it than show a wrong guess
- Date parsing handles day-month-year but not month-day-year, so some formats won't get picked up
- Corner detection struggles on busy/patterned backgrounds, can grab the wrong contour. Still usually fine since the code tries multiple versions of the image and picks whichever gives the best OCR confidence
- Can't fix folded/curved receipts since the correction is a flat transform, not 3D
- Total detection looks for "total" near a number, prefers "Grand Total" if present, otherwise picks the last matching line. Unusual layouts can still trip it up
- Tesseract path is hardcoded for windows in ocr_raw.py right now

## Challenges

Biggest one was OCR noise, phone photos are angled, blurry, have shadows, so raw OCR is pretty bad most of the time. Spent a lot of time on preprocessing (grayscale, denoising, thresholding, deskewing) just to get it usable, and it still misreads stuff sometimes (O vs 0, 1 vs l).

Parsing was harder than expected too since every receipt is formatted differently. No standard layout, so the parsing logic is based on common patterns (total near the end, dates near the top) instead of anything rigid.

## What I'd improve with more time

- Auto merchant name extraction using position based heuristics
- Handle more date formats
- Better handling for busy backgrounds, maybe restrict corner search to the center of the image
- Custom categories instead of a fixed list
- Line item level parsing, not just the total

## Note on the "ML" part

This uses pretrained models (Tesseract, bart-large-mnli) instead of training from scratch, since I don't have a labeled dataset and training something wasn't realistic in the time I had. The actual work is in the preprocessing pipeline, tuning Tesseract, parsing messy OCR text, and combining the classifier with rule based overrides. So less "trained my own model" and more "built a full pipeline around existing models and made it work end to end."
