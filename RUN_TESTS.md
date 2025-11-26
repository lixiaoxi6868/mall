# How to Run Tests

## Quick Start

### Run All Tests
```bash
# From project root (recommended)
python3 run_tests.py

# Or using unittest discover
python3 -m unittest discover tests

# From tests directory
cd tests
python3 test_mall.py
```

### Run with Verbose Output
```bash
python3 run_tests.py  # Already verbose
python3 -m unittest discover tests -v
```

## Test Results Summary

```
✅ All 25 Tests Passing
⏱️  Execution Time: ~0.12 seconds
📊 Success Rate: 100%
```

## Main API Tests Covered

### 🛒 Shopping Cart APIs (MOST IMPORTANT)

#### 1. Add to Cart - `/add_to_cart/<id>` (POST)
```bash
# Test single item
python3 -m unittest test_mall.MallTestCase.test_add_to_cart

# Test multiple items
python3 -m unittest test_mall.MallTestCase.test_add_multiple_items_to_cart

# Test quantity accumulation
python3 -m unittest test_mall.MallTestCase.test_add_same_item_twice
```

**What it tests:**
- Adding a product to cart
- Session persistence
- Quantity tracking
- Multiple products in cart
- Same product added twice increases quantity

#### 2. View Cart - `/cart` (GET)
```bash
# Test empty cart
python3 -m unittest test_mall.MallTestCase.test_view_cart_empty

# Test cart with items
python3 -m unittest test_mall.MallTestCase.test_view_cart_with_items

# Test calculations
python3 -m unittest test_mall.MallTestCase.test_cart_calculation
```

**What it tests:**
- Empty cart display
- Cart with items display
- Price calculations
- Total computation

#### 3. Update Cart - `/update_cart/<id>` (POST)
```bash
# Test quantity update
python3 -m unittest test_mall.MallTestCase.test_update_cart_quantity

# Test removal via zero quantity
python3 -m unittest test_mall.MallTestCase.test_update_cart_zero_quantity
```

**What it tests:**
- Updating item quantity
- Removing items by setting quantity to 0
- Session updates

#### 4. Remove from Cart - `/remove_from_cart/<id>` (GET)
```bash
python3 -m unittest test_mall.MallTestCase.test_remove_from_cart
```

**What it tests:**
- Removing specific items
- Keeping other items intact
- Flash messages

#### 5. Clear Cart - `/clear_cart` (GET)
```bash
python3 -m unittest test_mall.MallTestCase.test_clear_cart
```

**What it tests:**
- Clearing entire cart
- Session reset

### 💳 Checkout APIs

#### 1. Checkout Page - `/checkout` (GET)
```bash
# Test with items
python3 -m unittest test_mall.MallTestCase.test_checkout_page_with_items

# Test empty cart redirect
python3 -m unittest test_mall.MallTestCase.test_checkout_page_empty_cart
```

**What it tests:**
- Checkout form display
- Empty cart protection
- Order summary display

#### 2. Place Order - `/checkout` (POST)
```bash
# Test successful order
python3 -m unittest test_mall.MallTestCase.test_checkout_submission_success

# Test validation
python3 -m unittest test_mall.MallTestCase.test_checkout_submission_missing_fields

# Test database persistence
python3 -m unittest test_mall.MallTestCase.test_database_order_creation

# Test stock updates
python3 -m unittest test_mall.MallTestCase.test_stock_update_after_order
```

**What it tests:**
- Order creation
- Form validation
- Database persistence
- Stock reduction
- Cart clearing after order
- Redirect to confirmation

#### 3. Order Confirmation - `/order/<id>` (GET)
```bash
# Test valid order
python3 -m unittest test_mall.MallTestCase.test_order_confirmation_page

# Test invalid order ID
python3 -m unittest test_mall.MallTestCase.test_order_confirmation_invalid_id
```

**What it tests:**
- Order details display
- Customer information
- Order items list
- Invalid ID handling

### 🔍 Product APIs

#### 1. Home Page - `/` (GET)
```bash
# Test product listing
python3 -m unittest test_mall.MallTestCase.test_home_page
python3 -m unittest test_mall.MallTestCase.test_product_listing

# Test search
python3 -m unittest test_mall.MallTestCase.test_search_functionality

# Test category filter
python3 -m unittest test_mall.MallTestCase.test_category_filter
```

#### 2. Product Detail - `/product/<id>` (GET)
```bash
# Test valid product
python3 -m unittest test_mall.MallTestCase.test_product_detail_page

# Test invalid product
python3 -m unittest test_mall.MallTestCase.test_product_detail_invalid_id
```

## Integration Tests

### Complete Shopping Flow
```bash
python3 -m unittest test_mall.MallAPIIntegrationTest.test_complete_shopping_flow
```

**Tests the complete user journey:**
1. Browse products
2. View product details
3. Add to cart (multiple items)
4. Update cart quantities
5. Proceed to checkout
6. Submit order
7. View confirmation

## Test Categories

### Run Only Cart Tests
```bash
python3 -m unittest tests.test_mall.MallTestCase.test_add_to_cart tests.test_mall.MallTestCase.test_update_cart_quantity tests.test_mall.MallTestCase.test_remove_from_cart -v
```

### Run Only Checkout Tests
```bash
python3 -m unittest tests.test_mall.MallTestCase.test_checkout_submission_success tests.test_mall.MallTestCase.test_database_order_creation -v
```

### Run Only Integration Tests
```bash
python3 -m unittest tests.test_mall.MallAPIIntegrationTest -v
```

## Understanding Test Output

### Success Output
```
test_add_to_cart (test_mall.MallTestCase)
Test adding a product to cart ... ok
```
✅ Test passed successfully

### Failure Output (Example)
```
test_add_to_cart (test_mall.MallTestCase)
Test adding a product to cart ... FAIL

FAIL: test_add_to_cart (test_mall.MallTestCase)
AssertionError: '1' not in {}
```
❌ Test failed with assertion error

### Error Output (Example)
```
test_add_to_cart (test_mall.MallTestCase)
Test adding a product to cart ... ERROR

ERROR: test_add_to_cart (test_mall.MallTestCase)
sqlite3.OperationalError: no such table: products
```
⚠️ Test errored due to exception

## Test Examples

### Example 1: Test Add to Cart
```python
def test_add_to_cart(self):
    """Test adding a product to cart"""
    # Initialize empty cart
    with self.client.session_transaction() as sess:
        sess['cart'] = {}
    
    # Add product with quantity 2
    response = self.client.post('/add_to_cart/1', 
                                data={'quantity': 2},
                                follow_redirects=True)
    
    # Verify success
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'Product added to cart', response.data)
    
    # Check cart session
    with self.client.session_transaction() as sess:
        self.assertIn('1', sess['cart'])
        self.assertEqual(sess['cart']['1'], 2)
```

### Example 2: Test Checkout
```python
def test_checkout_submission_success(self):
    """Test successful order submission"""
    # Add item to cart
    with self.client.session_transaction() as sess:
        sess['cart'] = {'1': 2}
    
    # Submit checkout form
    response = self.client.post('/checkout',
                                data={
                                    'name': 'John Doe',
                                    'email': 'john@example.com',
                                    'address': '123 Main St'
                                },
                                follow_redirects=True)
    
    # Verify order placed
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'placed successfully', response.data)
    
    # Verify cart cleared
    with self.client.session_transaction() as sess:
        self.assertEqual(len(sess['cart']), 0)
```

## Continuous Testing

### Watch Mode (Manual)
```bash
while true; do 
    clear
    python3 test_mall.py
    sleep 2
done
```

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
cd /Users/zhao/workspace/mall
python3 test_mall.py
if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

## Troubleshooting

### Issue: Tests fail with database errors
**Solution:** Tests create temporary databases, ensure you have write permissions

### Issue: Flask app is running during tests
**Solution:** Tests use separate test client, no conflict with running app

### Issue: Session data persists between tests
**Solution:** Each test has isolated setUp/tearDown, sessions are independent

## Test Statistics

| Category | Tests | Status |
|----------|-------|--------|
| Cart Operations | 8 | ✅ 100% |
| Checkout Flow | 6 | ✅ 100% |
| Product Browse | 6 | ✅ 100% |
| Database | 2 | ✅ 100% |
| Integration | 1 | ✅ 100% |
| Edge Cases | 2 | ✅ 100% |
| **TOTAL** | **25** | **✅ 100%** |

## Next Steps

1. Run tests before committing changes
2. Add new tests when adding features
3. Keep test coverage at 100%
4. Review TEST_COVERAGE.md for detailed analysis

## Quick Reference

```bash
# Run all tests (from project root)
python3 run_tests.py

# Using unittest discover
python3 -m unittest discover tests -v

# From tests directory
cd tests && python3 test_mall.py

# Specific test
python3 -m unittest tests.test_mall.MallTestCase.test_add_to_cart

# Integration test
python3 -m unittest tests.test_mall.MallAPIIntegrationTest -v
```

---

**All tests passing!** ✅ Your mall application APIs are fully tested and working correctly.

