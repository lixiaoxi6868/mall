# MyMall - Small Mall Application

A modern, feature-rich shopping mall web application built with Flask and SQLite.

## Features

- 🛍️ **Product Catalog**: Browse products across multiple categories (Electronics, Fashion, Home, Gaming)
- 🔍 **Search & Filter**: Search products by name and filter by category
- 🛒 **Shopping Cart**: Add, update, and remove products from cart
- 💳 **Checkout**: Simple checkout process with order confirmation
- 📦 **Order Management**: View order details and history
- 📱 **Responsive Design**: Beautiful, modern UI that works on all devices
- 💾 **Database**: SQLite database for products and orders

## Installation

1. Make sure you have Python 3.7+ installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the application:
```bash
python mall.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Browse Products
- View all products on the home page
- Use the search bar to find specific products
- Filter by category using the dropdown menu

### Shopping Cart
- Click "Add to Cart" on any product
- View your cart by clicking the cart icon in the navigation
- Update quantities or remove items as needed

### Checkout
- Click "Proceed to Checkout" from your cart
- Fill in your shipping information
- Place your order and receive a confirmation

## Project Structure

```
mall/
├── mall.py                 # Main application file
├── mall.db                 # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── run_tests.py           # Test runner script
├── README.md              # This file
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   └── order_confirmation.html
├── static/                # Static files
│   └── style.css          # Stylesheet
└── tests/                 # Test directory
    ├── __init__.py
    ├── test_mall.py       # Test suite
    └── README.md          # Test documentation
```

## Database Schema

### Products Table
- id (PRIMARY KEY)
- name
- category
- price
- description
- image_url (emoji icon)
- stock

### Orders Table
- id (PRIMARY KEY)
- customer_name
- customer_email
- customer_address
- total_amount
- order_date
- status

### Order Items Table
- id (PRIMARY KEY)
- order_id (FOREIGN KEY)
- product_id (FOREIGN KEY)
- product_name
- quantity
- price

## Sample Products

The application comes pre-loaded with 15 sample products across 4 categories:
- **Electronics**: iPhone, MacBook, AirPods, TV
- **Fashion**: Shoes, Jeans, Jacket, Watch
- **Home**: Coffee Maker, Blender, Air Purifier, Robot Vacuum
- **Gaming**: Gaming Mouse, Mechanical Keyboard, Gaming Headset

## Customization

### Adding More Products
You can add products directly through the database or modify the `init_db()` function in `mall.py`.

### Changing Styles
Edit `static/style.css` to customize the appearance.

### Secret Key
**Important**: Change the secret key in `mall.py` for production use:
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Templating**: Jinja2

## Features to Add (Future Enhancements)

- User authentication and accounts
- Product reviews and ratings
- Payment gateway integration
- Admin panel for product management
- Order tracking
- Wishlist functionality
- Email notifications
- Product images (replace emojis)

## License

This is a sample application for educational purposes.

## Support

For issues or questions, please create an issue in the repository.

Enjoy shopping! 🛍️
