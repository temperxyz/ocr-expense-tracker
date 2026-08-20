# just a quick script to dump some fake expenses into the db so the dashboard
# actually has stuff to show instead of like 2 data points. not real receipts,
# just testing data for the demo

import random
from datetime import date, timedelta
from db import init_db, insert_expense
from categorize import CATEGORIES

# fake merchant names, roughly matches the keyword overrides list in categorize.py
merchants = {
    "groceries": ["Carrefour", "Imtiaz Super Market", "Al Fatah", "Metro Cash & Carry", "Hyperstar"],
    "food & dining": ["Cheezious", "KFC", "McDonalds", "Dominos", "Foodpanda", "Ranchers"],
    "transport": ["Uber", "Careem", "Total Parco", "PSO Petrol", "Yango"],
    "utilities": ["WAPDA", "PTCL", "Sui Gas", "K-Electric"],
    "shopping": ["Khaadi", "Outfitters", "Daraz", "Al Fatah Mall", "J."],
    "entertainment": ["Cinepax", "Netflix", "Spotify", "Nueplex"],
    "other": ["ATM Withdrawal", "Misc Store", "Local Shop"],
}

def random_date():
    # random day sometime in the last 90 days, so the weekly trend chart
    # actually has more than 1 point
    d = date.today() - timedelta(days=random.randint(0, 90))
    return d.isoformat()

def seed(n=35):
    init_db()
    count = 0
    for i in range(n):
        category = random.choice(CATEGORIES)
        merchant = random.choice(merchants[category])
        total = round(random.uniform(150, 8000), 2)
        fake_date = random_date()
        raw_text = f"[demo data] {merchant} total {total}"
        # image_path has a UNIQUE constraint in db.py so every row needs a different fake path
        image_path = f"demo_seed/{merchant.replace(' ', '_')}_{i}.jpg"

        ok = insert_expense(merchant, fake_date, total, category, raw_text, image_path)
        if ok:
            count += 1

    print(f"inserted {count}/{n} fake expenses")

if __name__ == "__main__":
    seed(35)
