"""
SkinIntell Database Module
Handles SQLite database operations for Users, Products, Reviews, and ChatbotHistory
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_NAME = 'skinintel.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            skin_type TEXT,
            hair_type TEXT,
            issues TEXT,
            goal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            category TEXT,
            description TEXT
        )
    ''')
    
    # Reviews table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            source TEXT,
            review_text TEXT,
            rating INTEGER DEFAULT 5,
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )
    ''')
    
    # ChatbotHistory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ChatbotHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    ''')
    
    # SearchHistory table for tracking product searches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            search_term TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# ============== USER OPERATIONS ==============

def create_user(username, email, password, skin_type=None, hair_type=None, issues=None, goal=None):
    """Create a new user with hashed password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(password)
    
    try:
        cursor.execute('''
            INSERT INTO Users (username, email, password, skin_type, hair_type, issues, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, email, hashed_password, skin_type, hair_type, issues, goal))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        raise e

def get_user_by_email(email):
    """Get user by email address"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def verify_user(email, password):
    """Verify user credentials"""
    user = get_user_by_email(email)
    if user and check_password_hash(user['password'], password):
        return user
    return None

def update_user_profile(user_id, skin_type=None, hair_type=None, issues=None, goal=None):
    """Update user profile information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE Users 
        SET skin_type = ?, hair_type = ?, issues = ?, goal = ?
        WHERE id = ?
    ''', (skin_type, hair_type, issues, goal, user_id))
    
    conn.commit()
    conn.close()

# ============== PRODUCT OPERATIONS ==============

def add_product(name, price, category, description):
    """Add a new product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO Products (name, price, category, description)
        VALUES (?, ?, ?, ?)
    ''', (name, price, category, description))
    
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_product_by_id(product_id):
    """Get product by ID"""
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM Products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return product

def search_products(search_term, category=None, limit=20, offset=0):
    """Search products by name or description"""
    conn = get_db_connection()
    
    query = 'SELECT * FROM Products WHERE (name LIKE ? OR description LIKE ?)'
    params = [f'%{search_term}%', f'%{search_term}%']
    
    if category and category != 'all':
        query += ' AND category = ?'
        params.append(category)
    
    query += ' LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    products = conn.execute(query, params).fetchall()
    conn.close()
    return products

def get_products_by_category(category, limit=20):
    """Get products by category"""
    conn = get_db_connection()
    products = conn.execute(
        'SELECT * FROM Products WHERE category = ? LIMIT ?',
        (category, limit)
    ).fetchall()
    conn.close()
    return products

def get_product_count():
    """Get total number of products"""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM Products').fetchone()[0]
    conn.close()
    return count

def get_all_categories():
    """Get all unique product categories"""
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM Products').fetchall()
    conn.close()
    return [cat['category'] for cat in categories if cat['category']]

# ============== REVIEW OPERATIONS ==============

def add_review(product_id, source, review_text, rating=5):
    """Add a review for a product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO Reviews (product_id, source, review_text, rating)
        VALUES (?, ?, ?, ?)
    ''', (product_id, source, review_text, rating))
    
    conn.commit()
    review_id = cursor.lastrowid
    conn.close()
    return review_id

def get_reviews_for_product(product_id, limit=10):
    """Get reviews for a specific product"""
    conn = get_db_connection()
    reviews = conn.execute(
        'SELECT * FROM Reviews WHERE product_id = ? LIMIT ?',
        (product_id, limit)
    ).fetchall()
    conn.close()
    return reviews

# ============== CHATBOT HISTORY OPERATIONS ==============

def save_chatbot_query(user_id, query, response):
    """Save a chatbot interaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ChatbotHistory (user_id, query, response)
        VALUES (?, ?, ?)
    ''', (user_id, query, response))
    
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    return history_id

def get_user_chatbot_history(user_id, limit=10):
    """Get chatbot history for a user"""
    conn = get_db_connection()
    history = conn.execute(
        'SELECT * FROM ChatbotHistory WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
        (user_id, limit)
    ).fetchall()
    conn.close()
    return history

# ============== SEARCH HISTORY OPERATIONS ==============

def save_search_history(user_id, search_term):
    """Save a product search"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO SearchHistory (user_id, search_term)
        VALUES (?, ?)
    ''', (user_id, search_term))
    
    conn.commit()
    conn.close()

def get_user_search_history(user_id, limit=10):
    """Get search history for a user"""
    conn = get_db_connection()
    history = conn.execute(
        'SELECT * FROM SearchHistory WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
        (user_id, limit)
    ).fetchall()
    conn.close()
    return history

# ============== AI RECOMMENDATION ENGINE ==============

def get_recommended_products(skin_type=None, hair_type=None, issues=None, goal=None, limit=5):
    """
    Rule-based recommendation engine with category enforcement
    """
    conn = get_db_connection()
    
    conditions = []
    params = []
    
    # 1. Skin Type matches -> Strictly Skincare products
    if skin_type:
        term = skin_type.lower().strip()
        conditions.append("""
            (category IN ('Skincare', 'Face', 'Body', 'Moisturizers', 'Cleansers', 'Treatments') 
             AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?))
        """)
        params.extend([f'%{term}%', f'%{term}%'])

    # 2. Hair Type matches -> Strictly Haircare products
    if hair_type:
        term = hair_type.lower().strip()
        conditions.append("""
            (category IN ('Haircare', 'Shampoo', 'Conditioner', 'Styling') 
             AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?))
        """)
        params.extend([f'%{term}%', f'%{term}%'])
        
    # 3. Handle Issues and Goals (General terms)
    general_terms = []
    if issues: general_terms.extend(issues.lower().split(','))
    if goal: general_terms.extend(goal.lower().split())
    general_terms = [t.strip() for t in general_terms if t.strip()]

    for term in general_terms:
        # Heuristic: Detect category intent in the text
        if 'hair' in term or 'scalp' in term or 'frizz' in term or 'curl' in term:
             # Force Haircare
             conditions.append("""
                (category IN ('Haircare', 'Shampoo', 'Conditioner', 'Styling') 
                 AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?))
             """)
             params.extend([f'%{term}%', f'%{term}%'])
             
        elif 'skin' in term or 'face' in term or 'acne' in term or 'wrinkle' in term or 'pimple' in term:
             # Force Skincare
             conditions.append("""
                (category IN ('Skincare', 'Face', 'Body', 'Moisturizers', 'Cleansers', 'Treatments') 
                 AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?))
             """)
             params.extend([f'%{term}%', f'%{term}%'])
             
        else:
             # Neutral term - search everywhere
             conditions.append("(LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)")
             params.extend([f'%{term}%', f'%{term}%', f'%{term}%'])

    if not conditions:
        # Default: Random mix
        products = conn.execute(
            'SELECT * FROM Products ORDER BY RANDOM() LIMIT ?',
            (limit,)
        ).fetchall()
    else:
        # Combine all conditions with OR
        query = "SELECT * FROM Products WHERE " + " OR ".join(conditions) + " ORDER BY RANDOM() LIMIT ?"
        params.append(limit)  
        
        products = conn.execute(query, params).fetchall()
        
        # Fallback if specific search gave no results
        if len(products) < limit:
            remaining = limit - len(products)
            fallback = conn.execute(
                'SELECT * FROM Products ORDER BY RANDOM() LIMIT ?',
                (remaining,)
            ).fetchall()
            products = list(products) + list(fallback)
    
    conn.close()
    return products[:limit]

def generate_skincare_routine(skin_type, issues=None, goal=None):
    """Generate a basic skincare routine based on user profile"""
    
    routine = {
        "morning": [],
        "evening": []
    }
    
    # Morning routine
    routine["morning"] = [
        {"step": 1, "name": "Cleanser", "description": f"Gentle cleanser suitable for {skin_type or 'all'} skin"},
        {"step": 2, "name": "Toner", "description": "Hydrating toner to balance skin pH"},
        {"step": 3, "name": "Serum", "description": "Vitamin C serum for brightness and protection"},
        {"step": 4, "name": "Moisturizer", "description": f"Lightweight moisturizer for {skin_type or 'all'} skin"},
        {"step": 5, "name": "Sunscreen", "description": "SPF 30+ broad spectrum sunscreen (essential!)"}
    ]
    
    # Evening routine
    routine["evening"] = [
        {"step": 1, "name": "Makeup Remover/Oil Cleanser", "description": "Remove makeup and sunscreen"},
        {"step": 2, "name": "Cleanser", "description": f"Gentle cleanser for {skin_type or 'all'} skin"},
        {"step": 3, "name": "Toner", "description": "Hydrating or exfoliating toner"},
        {"step": 4, "name": "Treatment", "description": get_treatment_recommendation(issues)},
        {"step": 5, "name": "Moisturizer", "description": "Nourishing night cream or sleeping mask"}
    ]
    
    return routine

def get_treatment_recommendation(issues):
    """Get treatment recommendation based on skin issues"""
    if not issues:
        return "Hydrating serum or facial oil"
    
    issues_lower = issues.lower()
    
    if 'acne' in issues_lower or 'breakout' in issues_lower:
        return "Salicylic acid or benzoyl peroxide treatment"
    elif 'aging' in issues_lower or 'wrinkle' in issues_lower:
        return "Retinol or peptide serum"
    elif 'dark spot' in issues_lower or 'hyperpigmentation' in issues_lower:
        return "Niacinamide or alpha arbutin serum"
    elif 'dry' in issues_lower or 'dehydrat' in issues_lower:
        return "Hyaluronic acid serum"
    elif 'oily' in issues_lower:
        return "Niacinamide serum to control oil"
    else:
        return "Targeted treatment serum for your concerns"

def generate_haircare_routine(hair_type, issues=None, goal=None):
    """Generate a basic haircare routine based on user profile"""
    
    routine = {
        "wash_day": [],
        "maintenance": []
    }
    
    # Wash day routine
    routine["wash_day"] = [
        {"step": 1, "name": "Pre-wash Treatment", "description": "Optional oil treatment 30 min before wash"},
        {"step": 2, "name": "Shampoo", "description": f"Sulfate-free shampoo for {hair_type or 'all'} hair"},
        {"step": 3, "name": "Conditioner", "description": "Focus on mid-lengths to ends"},
        {"step": 4, "name": "Deep Conditioner", "description": "Weekly deep conditioning treatment"},
        {"step": 5, "name": "Leave-in", "description": "Leave-in conditioner or detangler"}
    ]
    
    # Maintenance routine
    routine["maintenance"] = [
        {"step": 1, "name": "Refresh", "description": "Water or leave-in spray to refresh"},
        {"step": 2, "name": "Protect", "description": "Heat protectant before any heat styling"},
        {"step": 3, "name": "Style", "description": "Styling products suitable for your hair type"},
        {"step": 4, "name": "Seal", "description": "Light oil or serum on ends to prevent breakage"}
    ]
    
    return routine


if __name__ == '__main__':
    init_db()
    print(f"Database '{DATABASE_NAME}' created with all tables.")
