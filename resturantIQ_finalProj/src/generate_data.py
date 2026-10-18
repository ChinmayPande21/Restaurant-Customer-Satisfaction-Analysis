from pathlib import Path
import random
import pandas as pd

BRANCHES = ["Downtown", "Riverside", "Tech Park", "Harbor View", "Old Town"]
CUISINES = ["Indian", "Italian", "Asian Fusion", "Mexican", "Mediterranean"]
DINING_TYPES = ["Dine-in", "Takeaway", "Delivery"]
POSITIVE = [
    "Wonderful meal with fresh ingredients and friendly staff.", "Quick service and delicious food; great value for money.",
    "The dining room was spotless and our order was accurate.", "Excellent flavors, warm service, and a relaxing atmosphere.",
]
NEGATIVE = [
    "We waited too long for our food and the service felt slow.", "The staff were dismissive and our order was incorrect.",
    "Food arrived cold and the portion did not feel worth the price.", "Tables and washroom needed better cleaning and hygiene.",
]
NEUTRAL = ["Food was okay and the service was average.", "A reasonable visit, though nothing stood out.", "The meal matched expectations for a casual restaurant."]

def generate_sample(path: str | Path = "data/sample_reviews.csv", n: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        rating = rng.choices([1, 2, 3, 4, 5], weights=[7, 10, 20, 34, 29])[0]
        if rating <= 2: text = rng.choice(NEGATIVE)
        elif rating == 3: text = rng.choice(NEUTRAL)
        else: text = rng.choice(POSITIVE)
        rows.append({
            "review_id": f"R{i:04d}", "date": pd.Timestamp("2025-01-01") + pd.Timedelta(rng.randint(0, 364), unit="D"),
            "branch": rng.choice(BRANCHES), "rating": rating, "review_text": text,
            "cuisine": rng.choice(CUISINES), "food_quality": max(1, min(5, rating + rng.choice([-1, 0, 0, 1]))),
            "service_rating": max(1, min(5, rating + rng.choice([-1, 0, 0, 1]))),
            "cleanliness_rating": max(1, min(5, rating + rng.choice([-1, 0, 0, 1]))),
            "price_rating": max(1, min(5, rating + rng.choice([-1, 0, 0, 1]))),
            "dining_type": rng.choice(DINING_TYPES),
        })
    df = pd.DataFrame(rows)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    generate_sample()
    print("Generated data/sample_reviews.csv")
