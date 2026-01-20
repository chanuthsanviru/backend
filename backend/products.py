from flask import Blueprint, request, jsonify
from models import db, Product
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    try:
        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            ))
        
        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        products = [product.to_dict() for product in paginated.items]
        
        return jsonify({
            'products': products,
            'total': paginated.total,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'pages': paginated.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        if not product.is_active:
            return jsonify({'error': 'Product is not available'}), 404
        
        return jsonify({
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/api/products/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Product.category).distinct().filter_by(is_active=True).all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints (protected)
@products_bp.route('/api/admin/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            category=data['category'],
            image_url=data.get('image_url'),
            stock_quantity=data.get('stock_quantity', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/api/admin/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'category' in data:
            product.category = data['category']
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'is_active' in data:
            product.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500