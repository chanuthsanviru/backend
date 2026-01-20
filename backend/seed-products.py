from app import create_app
from models import db, Product

def seed_products():
    app = create_app('development')
    
    with app.app_context():
        # Clear existing products
        Product.query.delete()
        
        # Add sample products
        products = [
            Product(
                name="Classic White T-Shirt",
                description="100% cotton, comfortable fit, perfect for everyday wear",
                price=24.99,
                category="T-Shirts",
                image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&auto=format&fit=crop",
                stock_quantity=100,
                is_active=True
            ),
            Product(
                name="Denim Jacket",
                description="Premium denim, slim fit, perfect for casual outings",
                price=89.99,
                category="Jackets",
                image_url="https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop",
                stock_quantity=50,
                is_active=True
            ),
            Product(
                name="Chino Pants",
                description="Comfortable chino pants, multiple colors available",
                price=59.99,
                category="Pants",
                image_url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop",
                stock_quantity=75,
                is_active=True
            ),
            Product(
                name="Hooded Sweatshirt",
                description="Warm and comfortable, perfect for colder days",
                price=49.99,
                category="Sweatshirts",
                image_url="https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500&auto=format&fit=crop",
                stock_quantity=60,
                is_active=True
            ),
            Product(
                name="Slim Fit Jeans",
                description="Modern slim fit, stretch denim for all-day comfort",
                price=79.99,
                category="Jeans",
                image_url="https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop",
                stock_quantity=80,
                is_active=True
            ),
            Product(
                name="Polo Shirt",
                description="Classic polo shirt, breathable fabric, perfect for smart casual",
                price=39.99,
                category="Shirts",
                image_url="https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=500&auto=format&fit=crop",
                stock_quantity=90,
                is_active=True
            ),
            Product(
                name="Bomber Jacket",
                description="Lightweight bomber jacket, water-resistant",
                price=99.99,
                category="Jackets",
                image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&auto=format&fit=crop",
                stock_quantity=40,
                is_active=True
            ),
            Product(
                name="Cargo Shorts",
                description="Utility cargo shorts with multiple pockets",
                price=44.99,
                category="Shorts",
                image_url="https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500&auto=format&fit=crop",
                stock_quantity=55,
                is_active=True
            ),
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        print(f"Seeded {len(products)} products successfully!")

if __name__ == '__main__':
    seed_products()