from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATABASE = 'mall.db'

def get_db():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with sample products"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 100
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            total_amount REAL NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Check if products exist, if not add sample data
    cursor.execute('SELECT COUNT(*) as count FROM products')
    if cursor.fetchone()['count'] == 0:
        sample_products = [
            ('iPhone 14 Pro', 'Electronics', 999.99, 'Latest Apple smartphone with A16 chip', '📱', 50),
            ('MacBook Pro 16"', 'Electronics', 2499.99, 'Powerful laptop for professionals', '💻', 30),
            ('AirPods Pro', 'Electronics', 249.99, 'Wireless earbuds with active noise cancellation', '🎧', 100),
            ('Samsung 4K TV', 'Electronics', 799.99, '55-inch smart TV with stunning display', '📺', 25),
            ('Nike Air Max', 'Fashion', 129.99, 'Comfortable running shoes', '👟', 75),
            ('Levi\'s Jeans', 'Fashion', 69.99, 'Classic denim jeans', '👖', 120),
            ('Leather Jacket', 'Fashion', 199.99, 'Premium leather jacket', '🧥', 40),
            ('Designer Watch', 'Fashion', 299.99, 'Elegant wristwatch', '⌚', 60),
            ('Coffee Maker', 'Home', 89.99, 'Automatic coffee machine', '☕', 80),
            ('Blender', 'Home', 59.99, 'High-speed blender for smoothies', '🥤', 90),
            ('Air Purifier', 'Home', 179.99, 'HEPA filter air purifier', '💨', 45),
            ('Robot Vacuum', 'Home', 349.99, 'Smart automated vacuum cleaner', '🤖', 35),
            ('Gaming Mouse', 'Gaming', 79.99, 'RGB gaming mouse with high DPI', '🖱️', 150),
            ('Mechanical Keyboard', 'Gaming', 129.99, 'RGB mechanical gaming keyboard', '⌨️', 100),
            ('Gaming Headset', 'Gaming', 99.99, '7.1 surround sound headset', '🎮', 85),
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, category, price, description, image_url, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page showing all products"""
    conn = get_db()
    cursor = conn.cursor()
    
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    
    if category != 'all':
        cursor.execute('SELECT * FROM products WHERE category = ? AND name LIKE ?', 
                      (category, f'%{search}%'))
    else:
        cursor.execute('SELECT * FROM products WHERE name LIKE ?', (f'%{search}%',))
    
    products = cursor.fetchall()
    
    # Get all categories
    cursor.execute('SELECT DISTINCT category FROM products')
    categories = [row['category'] for row in cursor.fetchall()]
    
    conn.close()
    
    # Initialize cart if not exists
    if 'cart' not in session:
        session['cart'] = {}
    
    return render_template('index.html', 
                         products=products, 
                         categories=categories,
                         current_category=category,
                         search_query=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Add product to shopping cart"""
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    session['cart'] = cart
    flash('Product added to cart!', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def view_cart():
    """View shopping cart"""
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_items=[], total=0)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT * FROM products WHERE id = ?', (int(product_id),))
        product = cursor.fetchone()
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': item_total
            })
            total += item_total
    
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    """Update quantity in cart"""
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' in session:
        product_id_str = str(product_id)
        if quantity > 0:
            session['cart'][product_id_str] = quantity
        else:
            session['cart'].pop(product_id_str, None)
        session.modified = True
    
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    """Remove product from cart"""
    if 'cart' in session:
        product_id_str = str(product_id)
        session['cart'].pop(product_id_str, None)
        session.modified = True
        flash('Product removed from cart!', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process"""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get customer information
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')
        
        if not all([name, email, address]):
            flash('Please fill in all fields!', 'error')
            return redirect(url_for('checkout'))
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Calculate total
        total = 0
        for product_id, quantity in session['cart'].items():
            cursor.execute('SELECT price FROM products WHERE id = ?', (int(product_id),))
            product = cursor.fetchone()
            if product:
                total += product['price'] * quantity
        
        # Create order
        cursor.execute('''
            INSERT INTO orders (customer_name, customer_email, customer_address, total_amount)
            VALUES (?, ?, ?, ?)
        ''', (name, email, address, total))
        
        order_id = cursor.lastrowid
        
        # Add order items
        for product_id, quantity in session['cart'].items():
            cursor.execute('SELECT name, price FROM products WHERE id = ?', (int(product_id),))
            product = cursor.fetchone()
            if product:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, int(product_id), product['name'], quantity, product['price']))
                
                # Update stock
                cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE id = ?
                ''', (quantity, int(product_id)))
        
        conn.commit()
        conn.close()
        
        # Clear cart
        session['cart'] = {}
        
        flash(f'Order #{order_id} placed successfully! Thank you for your purchase!', 'success')
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    # GET request - show checkout form
    conn = get_db()
    cursor = conn.cursor()
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        cursor.execute('SELECT * FROM products WHERE id = ?', (int(product_id),))
        product = cursor.fetchone()
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': item_total
            })
            total += item_total
    
    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    if not order:
        flash('Order not found!', 'error')
        return redirect(url_for('index'))
    
    cursor.execute('''
        SELECT * FROM order_items WHERE order_id = ?
    ''', (order_id,))
    order_items = cursor.fetchall()
    
    conn.close()
    
    return render_template('order_confirmation.html', order=order, order_items=order_items)

@app.route('/clear_cart')
def clear_cart():
    """Clear shopping cart"""
    session['cart'] = {}
    flash('Cart cleared!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

