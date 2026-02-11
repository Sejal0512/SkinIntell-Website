
"""
SkinIntell - Flask Web Application
AI-powered skincare and haircare recommendation platform
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import os
from datetime import datetime

# Import database module
from database import (
    init_db, create_user, verify_user, get_user_by_id, update_user_profile,
    search_products, get_product_by_id, get_reviews_for_product, get_product_count,
    get_all_categories, save_chatbot_query, get_user_chatbot_history,
    save_search_history, get_user_search_history, get_recommended_products,
    generate_skincare_routine, generate_haircare_routine,
    get_vegan_cf_products, get_vegan_cf_stats
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'skinintel-secret-key-2024')

# Initialize database on startup
init_db()

# ============== DECORATORS ==============

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============== PUBLIC ROUTES ==============

@app.route('/')
def landing():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')
        
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        skin_type = request.form.get('skin_type', '')
        hair_type = request.form.get('hair_type', '')
        issues = request.form.get('issues', '')
        goal = request.form.get('goal', '')
        
        # Validation
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')
        
        try:
            user_id = create_user(username, email, password, skin_type, hair_type, issues, goal)
            session['user_id'] = user_id
            session['username'] = username
            flash('Registration successful! Welcome to SkinIntell.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                flash('Email or username already exists.', 'danger')
            else:
                flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout handler"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

# ============== PROTECTED ROUTES ==============

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = get_user_by_id(session['user_id'])
    chatbot_history = get_user_chatbot_history(session['user_id'], limit=5)
    search_history = get_user_search_history(session['user_id'], limit=5)
    product_count = get_product_count()
    vegan_cf_products = get_vegan_cf_products(limit=6)
    vegan_cf_stats = get_vegan_cf_stats()
    
    return render_template('dashboard.html', 
                         user=user, 
                         chatbot_history=chatbot_history,
                         search_history=search_history,
                         product_count=product_count,
                         vegan_cf_products=vegan_cf_products,
                         vegan_cf_stats=vegan_cf_stats)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        skin_type = request.form.get('skin_type', '')
        hair_type = request.form.get('hair_type', '')
        issues = request.form.get('issues', '')
        goal = request.form.get('goal', '')
        
        update_user_profile(session['user_id'], skin_type, hair_type, issues, goal)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

@app.route('/chatbot')
@login_required
def chatbot():
    """AI Assistant / Chatbot page"""
    user = get_user_by_id(session['user_id'])
    history = get_user_chatbot_history(session['user_id'], limit=20)
    return render_template('chatbot.html', user=user, history=history)

@app.route('/review-radar')
@login_required
def review_radar():
    """Review Radar - Product search and reviews"""
    categories = get_all_categories()
    return render_template('review_radar.html', categories=categories)

# ============== API ROUTES ==============

@app.route('/api/chatbot', methods=['POST'])
@login_required
def api_chatbot():
    """API endpoint for chatbot queries"""
    data = request.get_json()
    
    skin_type = data.get('skin_type', '')
    hair_type = data.get('hair_type', '')
    issues = data.get('issues', '')
    goal = data.get('goal', '')
    query_type = data.get('query_type', 'products')  # 'products', 'skincare_routine', 'haircare_routine'
    vegan = data.get('vegan', False)
    cruelty_free = data.get('cruelty_free', False)
    
    # Build the query string for history
    prefs = []
    if vegan: prefs.append('Vegan')
    if cruelty_free: prefs.append('Cruelty-Free')
    pref_str = f", Preferences: {', '.join(prefs)}" if prefs else ''
    query = f"Skin: {skin_type}, Hair: {hair_type}, Issues: {issues}, Goal: {goal}, Type: {query_type}{pref_str}"
    
    response_data = {}
    
    if query_type == 'products':
        # Get recommended products
        products = get_recommended_products(skin_type, hair_type, issues, goal, limit=6, vegan=vegan, cruelty_free=cruelty_free)
        products_list = [dict(p) for p in products]
        response_data['products'] = products_list
        response_data['message'] = f"Based on your profile, here are {len(products_list)} recommended products for you!"
        if vegan or cruelty_free:
            filter_tags = []
            if vegan: filter_tags.append('🌿 Vegan')
            if cruelty_free: filter_tags.append('🐰 Cruelty-Free')
            response_data['message'] += f" (Filtered: {', '.join(filter_tags)})"
        response_text = f"Recommended {len(products_list)} products"
        
    elif query_type == 'skincare_routine':
        routine = generate_skincare_routine(skin_type, issues, goal)
        response_data['routine'] = routine
        response_data['message'] = "Here's your personalized skincare routine!"
        response_text = "Generated skincare routine"
        
    elif query_type == 'haircare_routine':
        routine = generate_haircare_routine(hair_type, issues, goal)
        response_data['routine'] = routine
        response_data['message'] = "Here's your personalized haircare routine!"
        response_text = "Generated haircare routine"
    
    else:
        # Default: get products
        products = get_recommended_products(skin_type, hair_type, issues, goal, limit=6, vegan=vegan, cruelty_free=cruelty_free)
        products_list = [dict(p) for p in products]
        response_data['products'] = products_list
        response_data['message'] = "Here are some product recommendations for you!"
        response_text = f"Recommended {len(products_list)} products"
    
    # Save to history
    save_chatbot_query(session['user_id'], query, response_text)
    
    return jsonify(response_data)

@app.route('/api/search-products', methods=['GET'])
@login_required
def api_search_products():
    """API endpoint for product search"""
    search_term = request.args.get('q', '').strip()
    category = request.args.get('category', 'all')
    page = int(request.args.get('page', 1))
    vegan = request.args.get('vegan', '0') == '1'
    cruelty_free = request.args.get('cruelty_free', '0') == '1'
    per_page = 12
    offset = (page - 1) * per_page
    
    if search_term:
        # Save search history
        save_search_history(session['user_id'], search_term)
        
        # Search products
        products = search_products(search_term, category, limit=per_page, offset=offset, vegan=vegan, cruelty_free=cruelty_free)
    else:
        # Return some random/featured products if no search term
        products = search_products('', category, limit=per_page, offset=offset, vegan=vegan, cruelty_free=cruelty_free)
    
    products_list = [dict(p) for p in products]
    
    return jsonify({
        'products': products_list,
        'page': page,
        'count': len(products_list)
    })

@app.route('/api/product/<int:product_id>', methods=['GET'])
@login_required
def api_get_product(product_id):
    """API endpoint to get product details with reviews"""
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    reviews = get_reviews_for_product(product_id, limit=10)
    
    return jsonify({
        'product': dict(product),
        'reviews': [dict(r) for r in reviews]
    })

@app.route('/api/user-stats', methods=['GET'])
@login_required
def api_user_stats():
    """API endpoint for user statistics"""
    chatbot_history = get_user_chatbot_history(session['user_id'], limit=100)
    search_history = get_user_search_history(session['user_id'], limit=100)
    
    return jsonify({
        'total_chatbot_queries': len(chatbot_history),
        'total_searches': len(search_history)
    })

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ============== MAIN ==============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

