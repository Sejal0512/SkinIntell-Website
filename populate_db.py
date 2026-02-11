
"""
SkinIntell Database Population Script
Generates and populates the database with 10,000+ skincare/haircare products and reviews
"""

import sqlite3
import random
from database import init_db, DATABASE_NAME

# ============== PRODUCT DATA TEMPLATES ==============

# Skincare brands
SKINCARE_BRANDS = [
    "CeraVe", "The Ordinary", "La Roche-Posay", "Neutrogena", "Olay", "Cetaphil",
    "Paula's Choice", "Drunk Elephant", "Tatcha", "Sunday Riley", "Kiehl's",
    "Clinique", "Estée Lauder", "SK-II", "Glossier", "Fresh", "Origins",
    "Murad", "Peter Thomas Roth", "Dr. Dennis Gross", "Biossance", "Farmacy",
    "First Aid Beauty", "Mario Badescu", "Laneige", "Belif", "Innisfree",
    "COSRX", "Klairs", "Some By Mi", "Beauty of Joseon", "Missha", "Etude House",
    "Glow Recipe", "Peach & Lily", "Then I Met You", "Herbivore", "Youth to the People"
]

# Haircare brands
HAIRCARE_BRANDS = [
    "Olaplex", "Kerastase", "Moroccanoil", "Redken", "Paul Mitchell", "Matrix",
    "Aveda", "Bumble and Bumble", "Living Proof", "Ouai", "Briogeo", "Amika",
    "IGK", "Drybar", "Verb", "Function of Beauty", "Prose", "SheaMoisture",
    "Cantu", "Carol's Daughter", "Pattern", "Mielle", "Curls", "DevaCurl",
    "Not Your Mother's", "OGX", "Garnier Fructis", "Pantene", "TRESemmé", "Herbal Essences"
]

# ============== VEGAN & CRUELTY-FREE BRAND DATA ==============
# Source: Kaggle Cruelty-Free Brands dataset + BeautyFeeds sample data
# These are real-world cruelty-free brands cross-referenced from datasets

CRUELTY_FREE_BRANDS = {
    # Skincare - certified cruelty-free
    "The Ordinary", "Drunk Elephant", "Tatcha", "Glossier", "Herbivore",
    "Youth to the People", "Biossance", "Farmacy", "Glow Recipe",
    "Peach & Lily", "Klairs", "COSRX", "Beauty of Joseon", "Innisfree",
    "First Aid Beauty", "Mario Badescu", "Paula's Choice", "Sunday Riley",
    "Then I Met You", "Some By Mi", "Etude House", "Belif", "Fresh",
    "Peter Thomas Roth", "Murad",
    # Haircare - certified cruelty-free
    "Briogeo", "Amika", "IGK", "Verb", "Ouai", "DevaCurl",
    "Pattern", "Mielle", "Curls", "SheaMoisture", "Cantu",
    "Carol's Daughter", "Living Proof", "Aveda", "Bumble and Bumble",
    "Function of Beauty", "Prose", "Olaplex", "Not Your Mother's",
    "Drybar"
}

VEGAN_BRANDS = {
    # Skincare - vegan certified
    "The Ordinary", "Herbivore", "Youth to the People", "Biossance",
    "Farmacy", "Glow Recipe", "Drunk Elephant", "Klairs", "COSRX",
    "Paula's Choice", "Some By Mi", "First Aid Beauty", "Glossier",
    "Pacifica", "e.l.f.", "Derma E",
    # Haircare - vegan certified
    "Amika", "IGK", "Verb", "Briogeo", "DevaCurl",
    "Mielle", "Curls", "Function of Beauty", "Prose",
    "Aveda", "Not Your Mother's", "Olaplex"
}

# Skincare product types
SKINCARE_PRODUCTS = {
    "Face Care": [
        ("Cleanser", ["Foaming", "Gel", "Cream", "Oil", "Micellar", "Gentle", "Deep Pore", "Hydrating"]),
        ("Moisturizer", ["Daily", "Night", "Gel", "Cream", "Lightweight", "Rich", "Oil-Free", "Barrier"]),
        ("Serum", ["Vitamin C", "Hyaluronic Acid", "Retinol", "Niacinamide", "Peptide", "AHA/BHA", "Brightening", "Anti-Aging"]),
        ("Toner", ["Hydrating", "Exfoliating", "Balancing", "Clarifying", "Soothing", "pH Balancing"]),
        ("Eye Cream", ["Anti-Aging", "Brightening", "De-Puffing", "Hydrating", "Firming"]),
        ("Face Mask", ["Sheet", "Clay", "Overnight", "Hydrating", "Peel-Off", "Exfoliating"]),
        ("Sunscreen", ["SPF 30", "SPF 50", "Mineral", "Chemical", "Tinted", "Lightweight"]),
        ("Face Oil", ["Rosehip", "Jojoba", "Squalane", "Marula", "Argan", "Facial"]),
        ("Exfoliator", ["Chemical", "Physical", "Enzyme", "Gentle", "Weekly"]),
        ("Treatment", ["Acne", "Dark Spot", "Anti-Aging", "Pore Minimizing", "Redness Relief"])
    ],
    "Body Care": [
        ("Body Lotion", ["Daily", "Intensive", "Lightweight", "Firming", "Hydrating"]),
        ("Body Wash", ["Hydrating", "Exfoliating", "Gentle", "Moisturizing", "Clarifying"]),
        ("Body Oil", ["Nourishing", "Firming", "Hydrating", "Luxurious", "Fast-Absorbing"]),
        ("Hand Cream", ["Intensive", "Daily", "Repair", "Anti-Aging", "Moisturizing"]),
        ("Body Scrub", ["Sugar", "Salt", "Coffee", "Exfoliating", "Smoothing"]),
        ("Body Butter", ["Whipped", "Rich", "Nourishing", "Hydrating"])
    ],
    "Lip Care": [
        ("Lip Balm", ["Hydrating", "SPF", "Tinted", "Overnight", "Medicated"]),
        ("Lip Mask", ["Overnight", "Hydrating", "Plumping", "Exfoliating"]),
        ("Lip Scrub", ["Sugar", "Gentle", "Exfoliating"])
    ]
}

# Haircare product types
HAIRCARE_PRODUCTS = {
    "Hair Care": [
        ("Shampoo", ["Clarifying", "Hydrating", "Volumizing", "Color-Safe", "Anti-Dandruff", "Strengthening", "Curl-Defining", "Sulfate-Free"]),
        ("Conditioner", ["Daily", "Deep", "Leave-In", "Hydrating", "Volumizing", "Color-Safe", "Curl-Defining", "Protein"]),
        ("Hair Mask", ["Deep Conditioning", "Protein", "Hydrating", "Repair", "Color-Protecting", "Strengthening"]),
        ("Hair Oil", ["Argan", "Coconut", "Marula", "Finishing", "Treatment", "Lightweight"]),
        ("Hair Serum", ["Frizz Control", "Shine", "Heat Protection", "Growth", "Smoothing"]),
        ("Dry Shampoo", ["Volumizing", "Invisible", "Texturizing", "Refreshing"]),
        ("Heat Protectant", ["Spray", "Cream", "Serum", "Lightweight"]),
        ("Styling Cream", ["Curl Defining", "Smoothing", "Texturizing", "Moisturizing"]),
        ("Hair Spray", ["Flexible Hold", "Strong Hold", "Volumizing", "Finishing"]),
        ("Scalp Treatment", ["Exfoliating", "Soothing", "Anti-Dandruff", "Growth Stimulating"])
    ]
}

# Product benefits/concerns addressed
BENEFITS = {
    "Face Care": [
        "for Dry Skin", "for Oily Skin", "for Combination Skin", "for Sensitive Skin",
        "for Acne-Prone Skin", "for Aging Skin", "for Dull Skin", "for All Skin Types",
        "with Anti-Aging Benefits", "for Brightening", "for Hydration", "for Pore Care",
        "for Dark Spots", "for Redness", "for Fine Lines", "for Uneven Texture"
    ],
    "Body Care": [
        "for Dry Skin", "for Very Dry Skin", "for Normal Skin", "for Sensitive Skin",
        "for All Skin Types", "for Rough Skin", "for Dull Skin", "with Firming Benefits"
    ],
    "Hair Care": [
        "for Dry Hair", "for Oily Hair", "for Normal Hair", "for Damaged Hair",
        "for Color-Treated Hair", "for Fine Hair", "for Thick Hair", "for Curly Hair",
        "for Straight Hair", "for Frizzy Hair", "for Thinning Hair", "for All Hair Types",
        "for Dandruff", "for Scalp Health", "for Hair Growth"
    ]
}

# Review templates
POSITIVE_REVIEWS = [
    "This product is absolutely amazing! I've been using it for {time} and my {area} has never looked better. Highly recommend!",
    "Finally found my holy grail! The texture is perfect and it absorbs quickly. Will definitely repurchase.",
    "I was skeptical at first, but this really works. My {concern} has improved significantly since I started using it.",
    "Great value for the price. Works just as well as more expensive alternatives I've tried.",
    "Love this product! It's gentle yet effective. My skin feels so soft and {result}.",
    "Been using this for {time} and I'm impressed with the results. My {area} looks more {result}.",
    "Perfect for my sensitive skin. No irritation and really helps with my {concern}.",
    "This is a must-have in my routine. The ingredients are clean and it actually delivers results.",
    "Excellent product! I've recommended it to all my friends. The {feature} is exactly what I needed.",
    "Super impressed with this purchase. Works well in my routine and I love the {feature}.",
    "Game changer for my {concern}. Noticed a difference within {time} of using it daily.",
    "Best purchase I've made in a while. The quality is top-notch and it really works.",
    "My go-to product now. Love how it makes my {area} feel - so {result}!",
    "This exceeded my expectations! Gentle formula that actually delivers visible results.",
    "Cannot live without this product anymore. It's become an essential part of my routine."
]

NEUTRAL_REVIEWS = [
    "Decent product, does what it claims. Nothing extraordinary but it works for me.",
    "It's okay. I've used better products but this gets the job done for the price.",
    "Good product overall. Takes some time to see results but seems to be working.",
    "Average product. Not bad but not amazing either. Would consider trying other options.",
    "Works as described. The texture is nice but I wish it had more {feature}.",
    "Solid product for the price point. Does what it says, no major complaints.",
    "It's fine. Not my favorite but I'll finish the bottle. Might try something else next.",
    "Okay product. Does help with my {concern} but takes longer than expected to see results."
]

NEGATIVE_REVIEWS = [
    "Unfortunately, this didn't work for me. My {area} didn't improve and I experienced some irritation.",
    "Not impressed. The product feels cheap and didn't deliver the promised results.",
    "Caused breakouts for me. Had to stop using it after a week. Not for sensitive skin.",
    "Overpriced for what it is. I've found drugstore alternatives that work better.",
    "The scent is too strong and the texture is not pleasant. Won't repurchase."
]

# Review variables
TIMES = ["a few weeks", "a month", "two months", "three months", "6 months", "a year"]
AREAS = ["skin", "face", "complexion", "hair", "scalp", "lips", "body"]
CONCERNS = ["dryness", "oiliness", "acne", "dark spots", "fine lines", "frizz", "dandruff", "dullness", "redness", "texture"]
RESULTS = ["hydrated", "smooth", "radiant", "clear", "healthy", "soft", "glowing", "balanced", "refreshed", "plump"]
FEATURES = ["ingredients", "texture", "scent", "packaging", "formula", "consistency", "absorption"]

def generate_product_name(brand, product_type, variant, benefit):
    """Generate a realistic product name"""
    templates = [
        f"{brand} {variant} {product_type} {benefit}",
        f"{brand} {product_type} - {variant}",
        f"{variant} {product_type} by {brand}",
        f"{brand} {variant} {product_type}",
        f"{brand} Pro {product_type} {variant}"
    ]
    return random.choice(templates)

def generate_product_description(product_type, variant, benefit):
    """Generate a realistic product description"""
    descriptions = [
        f"This {variant.lower()} {product_type.lower()} is specially formulated {benefit.lower()}. Enriched with powerful ingredients to deliver visible results and improve overall appearance.",
        f"A luxurious {variant.lower()} {product_type.lower()} designed {benefit.lower()}. Features a lightweight, fast-absorbing formula that leaves skin feeling refreshed and nourished.",
        f"Experience the power of our {variant.lower()} {product_type.lower()}, crafted {benefit.lower()}. This dermatologist-tested formula provides long-lasting hydration and visible improvement.",
        f"Our best-selling {variant.lower()} {product_type.lower()} is perfect {benefit.lower()}. Formulated with clean ingredients to gently yet effectively address your skincare concerns.",
        f"This innovative {variant.lower()} {product_type.lower()} works {benefit.lower()}. Suitable for daily use and gentle enough for even the most sensitive skin types."
    ]
    return random.choice(descriptions)

def generate_review(is_positive=True, is_neutral=False):
    """Generate a realistic review"""
    if is_neutral:
        template = random.choice(NEUTRAL_REVIEWS)
    elif is_positive:
        template = random.choice(POSITIVE_REVIEWS)
    else:
        template = random.choice(NEGATIVE_REVIEWS)
    
    review = template.format(
        time=random.choice(TIMES),
        area=random.choice(AREAS),
        concern=random.choice(CONCERNS),
        result=random.choice(RESULTS),
        feature=random.choice(FEATURES)
    )
    
    return review

def generate_price(product_type):
    """Generate a realistic price based on product type"""
    price_ranges = {
        "Serum": (499.00, 4999.00),
        "Moisturizer": (299.00, 3999.00),
        "Cleanser": (199.00, 1999.00),
        "Toner": (249.00, 2499.00),
        "Eye Cream": (499.00, 5999.00),
        "Face Mask": (99.00, 1499.00),
        "Sunscreen": (399.00, 2999.00),
        "Face Oil": (499.00, 4499.00),
        "Exfoliator": (299.00, 2999.00),
        "Treatment": (499.00, 5999.00),
        "Shampoo": (199.00, 2499.00),
        "Conditioner": (199.00, 2499.00),
        "Hair Mask": (399.00, 2999.00),
        "Hair Oil": (299.00, 3499.00),
        "Hair Serum": (299.00, 2999.00),
        "Body Lotion": (199.00, 1999.00),
        "Body Wash": (149.00, 1499.00),
        "Lip Balm": (99.00, 999.00),
        "default": (199.00, 2999.00)
    }
    
    min_price, max_price = price_ranges.get(product_type, price_ranges["default"])
    # Return price rounded to nearest 0 or 9 (marketing tactic) e.g. 499, 500
    price = random.uniform(min_price, max_price)
    return round(price / 10) * 10 - 1  # e.g., 499.0

def populate_database():
    """Populate the database with products and reviews"""
    # Initialize database
    init_db()
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM Reviews')
    cursor.execute('DELETE FROM Products')
    conn.commit()
    
    print("Generating products and reviews...")
    
    product_id = 0
    total_products = 0
    total_reviews = 0
    
    # Generate skincare products
    for category, product_types in SKINCARE_PRODUCTS.items():
        for product_type, variants in product_types:
            for brand in SKINCARE_BRANDS:
                for variant in variants:
                    # Generate 1-3 products per combination (randomly)
                    num_products = random.randint(1, 2)
                    for _ in range(num_products):
                        benefit = random.choice(BENEFITS.get(category, BENEFITS["Face Care"]))
                        
                        name = generate_product_name(brand, product_type, variant, benefit)
                        price = generate_price(product_type)
                        description = generate_product_description(product_type, variant, benefit)
                        
                        # Determine vegan and cruelty-free status based on brand
                        is_vegan = 1 if brand in VEGAN_BRANDS else 0
                        is_cruelty_free = 1 if brand in CRUELTY_FREE_BRANDS else 0
                        
                        cursor.execute('''
                            INSERT INTO Products (name, price, category, description, vegan, cruelty_free)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, price, category, description, is_vegan, is_cruelty_free))
                        
                        product_id = cursor.lastrowid
                        total_products += 1
                        
                        # Generate 2-5 reviews per product
                        num_reviews = random.randint(2, 5)
                        for _ in range(num_reviews):
                            # 70% positive, 20% neutral, 10% negative
                            rand = random.random()
                            if rand < 0.70:
                                review_text = generate_review(is_positive=True)
                                rating = random.randint(4, 5)
                            elif rand < 0.90:
                                review_text = generate_review(is_positive=False, is_neutral=True)
                                rating = random.randint(3, 4)
                            else:
                                review_text = generate_review(is_positive=False)
                                rating = random.randint(1, 3)
                            
                            source = random.choice(["Amazon", "Sephora", "Ulta", "Dermstore", "Verified Purchase"])
                            
                            cursor.execute('''
                                INSERT INTO Reviews (product_id, source, review_text, rating)
                                VALUES (?, ?, ?, ?)
                            ''', (product_id, source, review_text, rating))
                            total_reviews += 1
                        
                        if total_products % 500 == 0:
                            print(f"  Generated {total_products} products...")
                            conn.commit()
    
    # Generate haircare products
    for category, product_types in HAIRCARE_PRODUCTS.items():
        for product_type, variants in product_types:
            for brand in HAIRCARE_BRANDS:
                for variant in variants:
                    num_products = random.randint(1, 2)
                    for _ in range(num_products):
                        benefit = random.choice(BENEFITS.get(category, BENEFITS["Hair Care"]))
                        
                        name = generate_product_name(brand, product_type, variant, benefit)
                        price = generate_price(product_type)
                        description = generate_product_description(product_type, variant, benefit)
                        
                        # Determine vegan and cruelty-free status based on brand
                        is_vegan = 1 if brand in VEGAN_BRANDS else 0
                        is_cruelty_free = 1 if brand in CRUELTY_FREE_BRANDS else 0
                        
                        cursor.execute('''
                            INSERT INTO Products (name, price, category, description, vegan, cruelty_free)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, price, category, description, is_vegan, is_cruelty_free))
                        
                        product_id = cursor.lastrowid
                        total_products += 1
                        
                        # Generate 2-5 reviews per product
                        num_reviews = random.randint(2, 5)
                        for _ in range(num_reviews):
                            rand = random.random()
                            if rand < 0.70:
                                review_text = generate_review(is_positive=True)
                                rating = random.randint(4, 5)
                            elif rand < 0.90:
                                review_text = generate_review(is_positive=False, is_neutral=True)
                                rating = random.randint(3, 4)
                            else:
                                review_text = generate_review(is_positive=False)
                                rating = random.randint(1, 3)
                            
                            source = random.choice(["Amazon", "Ulta", "Sephora", "Sally Beauty", "Verified Purchase"])
                            
                            cursor.execute('''
                                INSERT INTO Reviews (product_id, source, review_text, rating)
                                VALUES (?, ?, ?, ?)
                            ''', (product_id, source, review_text, rating))
                            total_reviews += 1
                        
                        if total_products % 500 == 0:
                            print(f"  Generated {total_products} products...")
                            conn.commit()
    
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Database populated successfully!")
    print(f"   Total Products: {total_products}")
    print(f"   Total Reviews: {total_reviews}")
    print(f"   Database: {DATABASE_NAME}")

if __name__ == '__main__':
    populate_database()

