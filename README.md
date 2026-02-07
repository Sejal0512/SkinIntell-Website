# SkinIntell - AI Skincare & Haircare Assistant

![SkinIntell Logo](https://img.shields.io/badge/SkinIntell-AI%20Beauty%20Assistant-8b5cf6?style=for-the-badge)

A fully functional, beginner-friendly web application that provides personalized skincare and haircare recommendations powered by AI technology.

## ✨ Features

### 🤖 AI Assistant
- Get personalized product recommendations based on your skin type, hair type, and concerns
- Receive custom skincare and haircare routines tailored to your needs
- Interactive chat interface with history tracking

### 🔍 Review Radar
- Search through 10,000+ skincare and haircare products
- Read real customer reviews and ratings
- Filter products by category
- View detailed product information

### 📊 Dashboard
- Track your recent AI interactions
- View your search history
- Quick access to all features
- Profile summary at a glance

### 👤 User Profile
- Customize your beauty profile
- Save your skin type, hair type, concerns, and goals
- Get more accurate recommendations based on your profile

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/skinintell.git
   cd skinintell
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Populate the database**
   ```bash
   python populate_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
skinintell/
├── app.py                 # Main Flask application
├── database.py            # Database operations and AI logic
├── populate_db.py         # Database population script
├── requirements.txt       # Python dependencies
├── render.yaml            # Render.com deployment config
├── skinintel.db          # SQLite database (generated)
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # Client-side JavaScript
└── templates/
    ├── base.html          # Base template with sidebar
    ├── landing.html       # Landing page
    ├── login.html         # Login form
    ├── register.html      # Registration form
    ├── dashboard.html     # User dashboard
    ├── chatbot.html       # AI Assistant interface
    ├── review_radar.html  # Product search & reviews
    ├── profile.html       # User profile page
    ├── 404.html           # Not found error page
    └── 500.html           # Server error page
```

## 🗄️ Database Schema

### Users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| email | TEXT | Unique email address |
| password | TEXT | Hashed password |
| skin_type | TEXT | User's skin type |
| hair_type | TEXT | User's hair type |
| issues | TEXT | Skin/hair concerns |
| goal | TEXT | Beauty goals |
| created_at | TIMESTAMP | Account creation date |

### Products
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Product name |
| price | REAL | Product price |
| category | TEXT | Product category |
| description | TEXT | Product description |

### Reviews
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| product_id | INTEGER | Foreign key to Products |
| source | TEXT | Review source |
| review_text | TEXT | Review content |
| rating | INTEGER | Star rating (1-5) |

### ChatbotHistory
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to Users |
| query | TEXT | User's query |
| response | TEXT | AI response |
| timestamp | TIMESTAMP | Query timestamp |

## 🌐 Deployment

### Deploy to Render.com

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/skinintell.git
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Create Web Service"

3. **Your app will be live!**
   - Render will provide a URL like `https://skinintel.onrender.com`

### Environment Variables

For production, set these environment variables:
- `SECRET_KEY`: A secure random string for session encryption

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Bootstrap 5
- **Icons**: Bootstrap Icons
- **Fonts**: Google Fonts (Inter, Playfair Display)

## 📝 Usage Guide

### Register & Login
1. Click "Get Started" on the landing page
2. Fill in your details including optional beauty profile information
3. Log in with your email and password

### Using the AI Assistant
1. Navigate to "AI Assistant" in the sidebar
2. Fill in your skin type, hair type, concerns, and goals
3. Select what you want: Products, Skincare Routine, or Haircare Routine
4. Click "Get Recommendations"
5. View your personalized recommendations

### Searching Products
1. Navigate to "Review Radar" in the sidebar
2. Enter a product name or keyword in the search bar
3. Filter by category if needed
4. Click on a product to view details and reviews

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Product data inspired by various beauty retailers
- Icons by Bootstrap Icons
- Fonts by Google Fonts

---

Made with ❤️ for beautiful skin and hair
