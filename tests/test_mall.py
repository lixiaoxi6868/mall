"""
Unit tests and integration tests for Mall Application

This module contains comprehensive tests for:
- Product browsing and searching
- Shopping cart operations (add, update, remove)
- Checkout and order processing
- Database persistence
- Complete user flows
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path to import mall module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mall
from mall import app


class MallTestCase(unittest.TestCase):
    """Test cases for the Mall application"""
    
    def setUp(self):
        """Set up test client and database before each test"""
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Store original DATABASE value
        self.original_database = mall.DATABASE
        # Set test database path globally
        mall.DATABASE = self.db_path
        
        app.config['DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.client = app.test_client()
        
        # Initialize database with test data
        with app.app_context():
            mall.init_db()
    
    def tearDown(self):
        """Clean up after each test"""
        # Restore original DATABASE value
        mall.DATABASE = self.original_database
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MyMall', response.data)
        self.assertIn(b'Welcome to MyMall', response.data)
    
    def test_product_listing(self):
        """Test that products are displayed on home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'iPhone 14 Pro', response.data)
        self.assertIn(b'MacBook Pro', response.data)
    
    def test_category_filter(self):
        """Test filtering products by category"""
        response = self.client.get('/?category=Electronics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'iPhone 14 Pro', response.data)
        self.assertIn(b'Electronics', response.data)
    
    def test_search_functionality(self):
        """Test product search"""
        response = self.client.get('/?search=iPhone')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'iPhone', response.data)
    
    def test_product_detail_page(self):
        """Test product detail page"""
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add to Cart', response.data)
    
    def test_product_detail_invalid_id(self):
        """Test product detail with invalid ID"""
        response = self.client.get('/product/9999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product not found', response.data)
    
    def test_add_to_cart(self):
        """Test adding a product to cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {}
        
        response = self.client.post('/add_to_cart/1', 
                                    data={'quantity': 2},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product added to cart', response.data)
        
        # Check cart session
        with self.client.session_transaction() as sess:
            self.assertIn('1', sess['cart'])
            self.assertEqual(sess['cart']['1'], 2)
    
    def test_add_multiple_items_to_cart(self):
        """Test adding multiple different products to cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {}
        
        # Add first product
        self.client.post('/add_to_cart/1', data={'quantity': 1})
        # Add second product
        self.client.post('/add_to_cart/2', data={'quantity': 3})
        
        with self.client.session_transaction() as sess:
            self.assertEqual(len(sess['cart']), 2)
            self.assertEqual(sess['cart']['1'], 1)
            self.assertEqual(sess['cart']['2'], 3)
    
    def test_add_same_item_twice(self):
        """Test adding the same product twice increases quantity"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {}
        
        # Add product first time
        self.client.post('/add_to_cart/1', data={'quantity': 2})
        # Add same product again
        self.client.post('/add_to_cart/1', data={'quantity': 3})
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['cart']['1'], 5)  # 2 + 3
    
    def test_view_cart_empty(self):
        """Test viewing empty cart"""
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your cart is empty', response.data)
    
    def test_view_cart_with_items(self):
        """Test viewing cart with items"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2, '2': 1}
        
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shopping Cart', response.data)
        self.assertIn(b'Proceed to Checkout', response.data)
    
    def test_update_cart_quantity(self):
        """Test updating item quantity in cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        response = self.client.post('/update_cart/1', 
                                    data={'quantity': 5},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['cart']['1'], 5)
    
    def test_update_cart_zero_quantity(self):
        """Test that zero quantity removes item from cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        self.client.post('/update_cart/1', data={'quantity': 0})
        
        with self.client.session_transaction() as sess:
            self.assertNotIn('1', sess['cart'])
    
    def test_remove_from_cart(self):
        """Test removing an item from cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2, '2': 3}
        
        response = self.client.get('/remove_from_cart/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product removed from cart', response.data)
        
        with self.client.session_transaction() as sess:
            self.assertNotIn('1', sess['cart'])
            self.assertIn('2', sess['cart'])
    
    def test_clear_cart(self):
        """Test clearing the entire cart"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2, '2': 3, '3': 1}
        
        response = self.client.get('/clear_cart', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cart cleared', response.data)
        
        with self.client.session_transaction() as sess:
            self.assertEqual(len(sess['cart']), 0)
    
    def test_checkout_page_empty_cart(self):
        """Test that checkout redirects when cart is empty"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {}
        
        response = self.client.get('/checkout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your cart is empty', response.data)
    
    def test_checkout_page_with_items(self):
        """Test checkout page displays correctly with items"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Checkout', response.data)
        self.assertIn(b'Shipping Information', response.data)
    
    def test_checkout_submission_success(self):
        """Test successful order submission"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        response = self.client.post('/checkout',
                                    data={
                                        'name': 'John Doe',
                                        'email': 'john@example.com',
                                        'address': '123 Main St, City, State 12345'
                                    },
                                    follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # The flash message contains "placed successfully"
        self.assertIn(b'placed successfully', response.data)
        self.assertIn(b'Order Details', response.data)
        
        # Check that cart is cleared
        with self.client.session_transaction() as sess:
            self.assertEqual(len(sess['cart']), 0)
    
    def test_checkout_submission_missing_fields(self):
        """Test checkout fails with missing required fields"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        response = self.client.post('/checkout',
                                    data={
                                        'name': 'John Doe',
                                        'email': '',  # Missing email
                                        'address': '123 Main St'
                                    },
                                    follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill in all fields', response.data)
    
    def test_order_confirmation_page(self):
        """Test order confirmation page displays order details"""
        # First create an order
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2}
        
        response = self.client.post('/checkout',
                                    data={
                                        'name': 'Jane Smith',
                                        'email': 'jane@example.com',
                                        'address': '456 Oak Ave, Town, State 67890'
                                    },
                                    follow_redirects=False)
        
        # Extract order ID from redirect
        self.assertEqual(response.status_code, 302)
        order_id = response.location.split('/')[-1]
        
        # View confirmation page
        response = self.client.get(f'/order/{order_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order Placed Successfully', response.data)
        self.assertIn(b'Jane Smith', response.data)
        self.assertIn(b'jane@example.com', response.data)
    
    def test_order_confirmation_invalid_id(self):
        """Test viewing order with invalid ID"""
        response = self.client.get('/order/9999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order not found', response.data)
    
    def test_database_order_creation(self):
        """Test that orders are properly saved to database"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 1, '2': 2}
        
        self.client.post('/checkout',
                        data={
                            'name': 'Test User',
                            'email': 'test@example.com',
                            'address': 'Test Address'
                        })
        
        # Check database
        conn = mall.get_db()
        cursor = conn.cursor()
        
        # Check order exists
        cursor.execute('SELECT * FROM orders WHERE customer_email = ?', ('test@example.com',))
        order = cursor.fetchone()
        self.assertIsNotNone(order)
        self.assertEqual(order['customer_name'], 'Test User')
        
        # Check order items
        cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],))
        items = cursor.fetchall()
        self.assertEqual(len(items), 2)
        
        conn.close()
    
    def test_stock_update_after_order(self):
        """Test that product stock is updated after order"""
        # Get initial stock
        conn = mall.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT stock FROM products WHERE id = 1')
        initial_stock = cursor.fetchone()['stock']
        conn.close()
        
        # Place order
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 3}
        
        self.client.post('/checkout',
                        data={
                            'name': 'Stock Test',
                            'email': 'stock@example.com',
                            'address': 'Stock Address'
                        })
        
        # Check updated stock
        conn = mall.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT stock FROM products WHERE id = 1')
        updated_stock = cursor.fetchone()['stock']
        conn.close()
        
        self.assertEqual(updated_stock, initial_stock - 3)
    
    def test_cart_calculation(self):
        """Test that cart total is calculated correctly"""
        with self.client.session_transaction() as sess:
            sess['cart'] = {'1': 2, '3': 1}  # Product 1: $999.99 x 2, Product 3: $249.99 x 1
        
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        
        # Check if prices are displayed (allowing for formatting variations)
        self.assertIn(b'999.99', response.data)
        self.assertIn(b'249.99', response.data)


class MallAPIIntegrationTest(unittest.TestCase):
    """Integration tests for the complete user flow"""
    
    def setUp(self):
        """Set up test client and database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Store original DATABASE value
        self.original_database = mall.DATABASE
        # Set test database path globally
        mall.DATABASE = self.db_path
        
        app.config['DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        self.client = app.test_client()
        
        with app.app_context():
            mall.init_db()
    
    def tearDown(self):
        """Clean up"""
        # Restore original DATABASE value
        mall.DATABASE = self.original_database
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_complete_shopping_flow(self):
        """Test complete user journey from browsing to checkout"""
        # 1. Visit home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # 2. View product detail
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        
        # 3. Add product to cart
        response = self.client.post('/add_to_cart/1', data={'quantity': 2})
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # 4. Add another product
        self.client.post('/add_to_cart/2', data={'quantity': 1})
        
        # 5. View cart
        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        
        # 6. Update quantity
        self.client.post('/update_cart/1', data={'quantity': 3})
        
        # 7. Proceed to checkout
        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)
        
        # 8. Submit order
        response = self.client.post('/checkout',
                                    data={
                                        'name': 'Integration Test User',
                                        'email': 'integration@example.com',
                                        'address': '789 Integration Blvd'
                                    },
                                    follow_redirects=False)
        
        # 9. Check redirect to confirmation
        self.assertEqual(response.status_code, 302)
        self.assertIn('/order/', response.location)
        
        # 10. View confirmation
        response = self.client.get(response.location)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Order Placed Successfully', response.data)


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(MallTestCase))
    suite.addTests(loader.loadTestsFromTestCase(MallAPIIntegrationTest))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

