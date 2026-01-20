from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CartItem, Product
from sqlalchemy.orm import joinedload

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/api/cart', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        user_id = get_jwt_identity()
        
        cart_items = CartItem.query.options(
            joinedload(CartItem.product)
        ).filter_by(user_id=user_id).all()
        
        cart_data = [item.to_dict() for item in cart_items]
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product.price * item.quantity for item in cart_items if item.product)
        
        return jsonify({
            'cart_items': cart_data,
            'total_items': total_items,
            'total_price': float(total_price) if total_price else 0.0
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/api/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('product_id'):
            return jsonify({'error': 'Product ID is required'}), 400
        
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Check if product exists and is active
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return jsonify({'error': 'Product not found or unavailable'}), 404
        
        # Check stock
        if product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
            if product.stock_quantity < cart_item.quantity:
                return jsonify({'error': 'Insufficient stock for requested quantity'}), 400
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Item added to cart',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/api/cart/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({'error': 'Quantity is required'}), 400
        
        quantity = data['quantity']
        
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        # Check stock
        product = cart_item.product
        if product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'message': 'Cart item updated',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/api/cart/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    try:
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.filter_by(
            id=item_id,
            user_id=user_id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({
            'message': 'Item removed from cart'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cart_bp.route('/api/cart/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    try:
        user_id = get_jwt_identity()
        
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return jsonify({
            'message': 'Cart cleared'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500