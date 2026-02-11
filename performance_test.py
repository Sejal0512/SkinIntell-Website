import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def measure(name, func):
    start = time.time()
    try:
        result = func()
        duration = time.time() - start
        print(f"[{name}] Completed in {duration:.4f}s")
        return result
    except Exception as e:
        print(f"[{name}] Failed: {e}")
        return None

def run_tests():
    session = requests.Session()
    
    print("Waiting for server to ensure it is ready...")
    time.sleep(2)
    
    # 1. Home Page
    print("\n--- Testing Public Pages ---")
    measure("Home Page", lambda: session.get(BASE_URL))
    measure("Login Page", lambda: session.get(f"{BASE_URL}/login"))
    
    # 2. Registration (to get a session)
    print("\n--- Testing Authentication ---")
    username = f"perf_test_{int(time.time())}"
    email = f"{username}@example.com"
    password = "password123"
    
    def register():
        data = {
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
            "skin_type": "Oily",
            "hair_type": "Wavy"
        }
        return session.post(f"{BASE_URL}/register", data=data)

    measure("Registration", register)
    
    # 3. Protected Pages (Heavy Queries)
    print("\n--- Testing Heavy Queries ---")
    measure("Dashboard", lambda: session.get(f"{BASE_URL}/dashboard"))
    measure("Review Radar (Categories)", lambda: session.get(f"{BASE_URL}/review-radar"))
    
    # 4. Search API (tests DB indexing/speed)
    def search():
        return session.get(f"{BASE_URL}/api/search-products?q=serum").json()
        
    result = measure("Search API ('serum')", search)
    if result and 'products' in result:
        print(f"  Found {len(result['products'])} products")

if __name__ == "__main__":
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("Server not running. Please start app.py first.")
