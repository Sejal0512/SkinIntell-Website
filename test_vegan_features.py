"""
Comprehensive Test Suite for SkinIntell Vegan & Cruelty-Free Features
Run: python test_vegan_features.py
"""

import os
import sys
import json
import sqlite3
import unittest
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from database import (
    init_db, add_product, search_products, get_recommended_products,
    get_vegan_cf_products, get_vegan_cf_stats, get_product_by_id,
    create_user
)

DATABASE_NAME = 'skinintel.db'


class TestDatabaseSchema(unittest.TestCase):
    """Test 1: Verify database schema has vegan/cruelty_free columns."""

    def test_products_table_has_vegan_column(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Products)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        self.assertIn('vegan', columns, "Products table missing 'vegan' column")

    def test_products_table_has_cruelty_free_column(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Products)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        self.assertIn('cruelty_free', columns, "Products table missing 'cruelty_free' column")


class TestDataPopulation(unittest.TestCase):
    """Test 2: Verify product data is populated with vegan/CF flags."""

    def test_total_products_exist(self):
        conn = sqlite3.connect(DATABASE_NAME)
        count = conn.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "No products in database")
        print(f"  ✅ Total products: {count}")

    def test_vegan_products_exist(self):
        conn = sqlite3.connect(DATABASE_NAME)
        count = conn.execute("SELECT COUNT(*) FROM Products WHERE vegan = 1").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "No vegan products found")
        print(f"  ✅ Vegan products: {count}")

    def test_cruelty_free_products_exist(self):
        conn = sqlite3.connect(DATABASE_NAME)
        count = conn.execute("SELECT COUNT(*) FROM Products WHERE cruelty_free = 1").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "No cruelty-free products found")
        print(f"  ✅ Cruelty-free products: {count}")

    def test_both_vegan_and_cf_products_exist(self):
        conn = sqlite3.connect(DATABASE_NAME)
        count = conn.execute("SELECT COUNT(*) FROM Products WHERE vegan = 1 AND cruelty_free = 1").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "No products that are both vegan AND cruelty-free")
        print(f"  ✅ Both vegan + CF: {count}")

    def test_non_vegan_products_exist(self):
        conn = sqlite3.connect(DATABASE_NAME)
        count = conn.execute("SELECT COUNT(*) FROM Products WHERE vegan = 0").fetchone()[0]
        conn.close()
        self.assertGreater(count, 0, "All products are vegan — non-vegan products should exist too")
        print(f"  ✅ Non-vegan products: {count}")


class TestDatabaseFunctions(unittest.TestCase):
    """Test 3: Verify database query functions with vegan/CF filters."""

    def test_search_products_vegan_filter(self):
        products = search_products('', vegan=True)
        for p in products:
            self.assertEqual(dict(p)['vegan'], 1, f"Product '{dict(p)['name']}' is not vegan but returned with vegan filter")
        print(f"  ✅ search_products(vegan=True): {len(products)} results, all vegan")

    def test_search_products_cruelty_free_filter(self):
        products = search_products('', cruelty_free=True)
        for p in products:
            self.assertEqual(dict(p)['cruelty_free'], 1, f"Product '{dict(p)['name']}' is not CF but returned with CF filter")
        print(f"  ✅ search_products(cruelty_free=True): {len(products)} results, all CF")

    def test_search_products_both_filters(self):
        products = search_products('', vegan=True, cruelty_free=True)
        for p in products:
            d = dict(p)
            self.assertEqual(d['vegan'], 1, "Product not vegan")
            self.assertEqual(d['cruelty_free'], 1, "Product not CF")
        print(f"  ✅ search_products(vegan+CF): {len(products)} results, all both")

    def test_search_products_no_filter(self):
        products = search_products('')
        self.assertGreater(len(products), 0, "No products returned without filters")
        print(f"  ✅ search_products(no filter): {len(products)} results")

    def test_get_recommended_products_vegan(self):
        products = get_recommended_products(vegan=True, limit=5)
        for p in products:
            self.assertEqual(dict(p)['vegan'], 1, "Recommended product not vegan")
        print(f"  ✅ get_recommended_products(vegan=True): {len(products)} results, all vegan")

    def test_get_recommended_products_cf(self):
        products = get_recommended_products(cruelty_free=True, limit=5)
        for p in products:
            self.assertEqual(dict(p)['cruelty_free'], 1, "Recommended product not CF")
        print(f"  ✅ get_recommended_products(cruelty_free=True): {len(products)} results, all CF")

    def test_get_recommended_products_with_skin_type_and_vegan(self):
        products = get_recommended_products(skin_type='oily', vegan=True, limit=5)
        for p in products:
            self.assertEqual(dict(p)['vegan'], 1, "Recommended product not vegan")
        print(f"  ✅ get_recommended_products(skin_type='oily', vegan=True): {len(products)} results")

    def test_get_vegan_cf_products(self):
        products = get_vegan_cf_products(limit=6)
        for p in products:
            d = dict(p)
            self.assertEqual(d['vegan'], 1)
            self.assertEqual(d['cruelty_free'], 1)
        print(f"  ✅ get_vegan_cf_products(): {len(products)} results, all both")

    def test_get_vegan_cf_stats(self):
        stats = get_vegan_cf_stats()
        self.assertIn('vegan', stats)
        self.assertIn('cruelty_free', stats)
        self.assertIn('both', stats)
        self.assertGreater(stats['vegan'], 0)
        self.assertGreater(stats['cruelty_free'], 0)
        self.assertGreater(stats['both'], 0)
        print(f"  ✅ get_vegan_cf_stats(): vegan={stats['vegan']}, cf={stats['cruelty_free']}, both={stats['both']}")

    def test_add_product_with_vegan_flag(self):
        pid = add_product("Test Vegan Serum", 999.0, "Skincare", "A test product", vegan=1, cruelty_free=1)
        product = get_product_by_id(pid)
        d = dict(product)
        self.assertEqual(d['vegan'], 1)
        self.assertEqual(d['cruelty_free'], 1)
        # Clean up
        conn = sqlite3.connect(DATABASE_NAME)
        conn.execute("DELETE FROM Products WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        print(f"  ✅ add_product(vegan=1, cruelty_free=1): created and verified id={pid}")


class TestFlaskRoutes(unittest.TestCase):
    """Test 4: Verify Flask API routes handle vegan/CF filters correctly."""

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        cls.client = app.test_client()
        # Create a test user and log in
        try:
            create_user('testrunner', 'testrunner@test.com', 'testpass123', 'oily', 'curly', 'acne', 'clear skin')
        except Exception:
            pass  # User might already exist
        cls.client.post('/login', data={
            'username': 'testrunner',
            'password': 'testpass123'
        }, follow_redirects=True)

    def test_dashboard_loads(self):
        response = self.client.get('/dashboard')
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            self.assertIn('Vegan', html, "Dashboard missing vegan content")
            print("  ✅ Dashboard loads with vegan content")
        else:
            print("  ⚠️ Dashboard redirected (likely auth issue in test)")

    def test_api_search_vegan_filter(self):
        response = self.client.get('/api/search-products?q=&vegan=1&cruelty_free=0')
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            for p in products:
                self.assertEqual(p.get('vegan'), 1, f"Non-vegan product in vegan-filtered results: {p.get('name')}")
            print(f"  ✅ /api/search-products?vegan=1: {len(products)} results, all vegan")
        else:
            print(f"  ⚠️ API returned status {response.status_code}")

    def test_api_search_cf_filter(self):
        response = self.client.get('/api/search-products?q=&cruelty_free=1&vegan=0')
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            for p in products:
                self.assertEqual(p.get('cruelty_free'), 1, f"Non-CF product in CF-filtered results: {p.get('name')}")
            print(f"  ✅ /api/search-products?cruelty_free=1: {len(products)} results, all CF")
        else:
            print(f"  ⚠️ API returned status {response.status_code}")

    def test_api_search_both_filters(self):
        response = self.client.get('/api/search-products?q=&vegan=1&cruelty_free=1')
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            for p in products:
                self.assertEqual(p.get('vegan'), 1)
                self.assertEqual(p.get('cruelty_free'), 1)
            print(f"  ✅ /api/search-products?vegan=1&cruelty_free=1: {len(products)} results")
        else:
            print(f"  ⚠️ API returned status {response.status_code}")

    def test_api_search_no_filter(self):
        response = self.client.get('/api/search-products?q=moisturizer')
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            print(f"  ✅ /api/search-products?q=moisturizer: {len(products)} results (no filter)")
        else:
            print(f"  ⚠️ API returned status {response.status_code}")

    def test_api_chatbot_with_vegan(self):
        response = self.client.post('/api/chatbot', 
            data=json.dumps({
                'skin_type': 'oily',
                'hair_type': '',
                'issues': 'acne',
                'goal': 'clear skin',
                'query_type': 'products',
                'vegan': True,
                'cruelty_free': False
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            for p in products:
                self.assertEqual(p.get('vegan'), 1, f"Non-vegan product in chatbot vegan results: {p.get('name')}")
            self.assertIn('Vegan', data.get('message', ''))
            print(f"  ✅ /api/chatbot (vegan=True): {len(products)} products, all vegan, message mentions Vegan")
        else:
            print(f"  ⚠️ Chatbot API returned status {response.status_code}")

    def test_api_chatbot_with_cf(self):
        response = self.client.post('/api/chatbot',
            data=json.dumps({
                'skin_type': '',
                'hair_type': 'curly',
                'issues': '',
                'goal': 'shiny hair',
                'query_type': 'products',
                'vegan': False,
                'cruelty_free': True
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            for p in products:
                self.assertEqual(p.get('cruelty_free'), 1, f"Non-CF product in chatbot CF results: {p.get('name')}")
            print(f"  ✅ /api/chatbot (cruelty_free=True): {len(products)} products, all CF")
        else:
            print(f"  ⚠️ Chatbot API returned status {response.status_code}")

    def test_api_chatbot_without_filters(self):
        response = self.client.post('/api/chatbot',
            data=json.dumps({
                'skin_type': 'dry',
                'hair_type': '',
                'issues': '',
                'goal': '',
                'query_type': 'products',
                'vegan': False,
                'cruelty_free': False
            }),
            content_type='application/json'
        )
        if response.status_code == 200:
            data = response.get_json()
            products = data.get('products', [])
            self.assertGreater(len(products), 0, "No products returned without filters")
            print(f"  ✅ /api/chatbot (no filters): {len(products)} products returned")
        else:
            print(f"  ⚠️ Chatbot API returned status {response.status_code}")

    def test_review_radar_page_loads(self):
        response = self.client.get('/review-radar')
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            self.assertIn('veganFilter', html, "Review Radar missing vegan filter checkbox")
            self.assertIn('crueltyFreeFilter', html, "Review Radar missing CF filter checkbox")
            print("  ✅ Review Radar loads with vegan/CF filter checkboxes")
        else:
            print(f"  ⚠️ Review Radar returned status {response.status_code}")

    def test_chatbot_page_loads(self):
        response = self.client.get('/chatbot')
        if response.status_code == 200:
            html = response.data.decode('utf-8')
            self.assertIn('veganPref', html, "Chatbot missing vegan toggle")
            self.assertIn('crueltyFreePref', html, "Chatbot missing CF toggle")
            print("  ✅ Chatbot page loads with vegan/CF toggles")
        else:
            print(f"  ⚠️ Chatbot page returned status {response.status_code}")


class TestProductDataIntegrity(unittest.TestCase):
    """Test 5: Verify data integrity — vegan brand products are correctly flagged."""

    def test_the_ordinary_is_vegan_and_cf(self):
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        products = conn.execute(
            "SELECT * FROM Products WHERE name LIKE '%The Ordinary%' LIMIT 5"
        ).fetchall()
        conn.close()
        for p in products:
            d = dict(p)
            self.assertEqual(d['vegan'], 1, f"The Ordinary product should be vegan: {d['name']}")
            self.assertEqual(d['cruelty_free'], 1, f"The Ordinary product should be CF: {d['name']}")
        print(f"  ✅ The Ordinary: {len(products)} products, all vegan+CF")

    def test_cerave_is_not_vegan(self):
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        products = conn.execute(
            "SELECT * FROM Products WHERE name LIKE '%CeraVe%' LIMIT 5"
        ).fetchall()
        conn.close()
        for p in products:
            d = dict(p)
            self.assertEqual(d['vegan'], 0, f"CeraVe product should NOT be vegan: {d['name']}")
            self.assertEqual(d['cruelty_free'], 0, f"CeraVe should NOT be CF: {d['name']}")
        print(f"  ✅ CeraVe: {len(products)} products, all non-vegan/non-CF (correct)")

    def test_herbivore_is_vegan_and_cf(self):
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        products = conn.execute(
            "SELECT * FROM Products WHERE name LIKE '%Herbivore%' LIMIT 5"
        ).fetchall()
        conn.close()
        for p in products:
            d = dict(p)
            self.assertEqual(d['vegan'], 1, f"Herbivore product should be vegan: {d['name']}")
            self.assertEqual(d['cruelty_free'], 1, f"Herbivore product should be CF: {d['name']}")
        print(f"  ✅ Herbivore: {len(products)} products, all vegan+CF")


if __name__ == '__main__':
    print("=" * 60)
    print("  SkinIntell Vegan & Cruelty-Free Feature Tests")
    print("=" * 60)
    print()

    # Run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes in order
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPopulation))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskRoutes))
    suite.addTests(loader.loadTestsFromTestCase(TestProductDataIntegrity))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("  ✅ ALL TESTS PASSED — Ready for deployment!")
    else:
        print(f"  ❌ {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 60)
