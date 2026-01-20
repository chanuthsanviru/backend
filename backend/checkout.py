from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CartItem, Order, OrderItem, Product
from sqlalchemy.orm import joinedload
import random
import string
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)

def generate_order_number():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'DM-{timestamp}-{random_str}'

@checkout_bp.route('/api/checkout', methods=['POST'])
@jwt_required()
def create_order():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get shipping information
        required_shipping_fields = ['shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country']
        for field in required_shipping_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get cart items
        cart_items = CartItem.query.options(
            joinedload(CartItem.product)
        ).filter_by(user_id=user_id).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Check stock and calculate total
        total_amount = 0
        order_items_data = []
        
        for cart_item in cart_items:
            product = cart_item.product
            
            if not product or not product.is_active:
                return jsonify({'error': f'Product {product.name if product else "Unknown"} is unavailable'}), 400
            
            if product.stock_quantity < cart_item.quantity:
                return jsonify({
                    'error': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'
                }), 400
            
            item_total = product.price * cart_item.quantity
            total_amount += item_total
            
            order_items_data.append({
                'product': product,
                'quantity': cart_item.quantity,
                'price': product.price
            })
        
        # Create order
        order = Order(
            user_id=user_id,
            order_number=generate_order_number(),
            total_amount=total_amount,
            status='pending',
            shipping_address=data['shipping_address'],
            shipping_city=data['shipping_city'],
            shipping_state=data['shipping_state'],
            shipping_zip=data['shipping_zip'],
            shipping_country=data['shipping_country']
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items and update stock
        for item_data in order_items_data:
            product = item_data['product']
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=item_data['quantity']
            )
            db.session.add(order_item)
            
            # Update product stock
            product.stock_quantity -= item_data['quantity']
        
        # Clear cart
        CartItem.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/api/orders', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        user_id = get_jwt_identity()
        
        orders = Order.query.filter_by(user_id=user_id).order_by(
            Order.created_at.desc()
        ).all()
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = get_jwt_identity()
        
        order = Order.query.filter_by(
            id=order_id,
            user_id=user_id
        ).first()
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin endpoints
@checkout_bp.route('/api/admin/orders', methods=['GET'])
def get_all_orders():
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        paginated = query.order_by(
            Order.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        orders = [order.to_dict() for order in paginated.items]
        
        return jsonify({
            'orders': orders,
            'total': paginated.total,
            'page': paginated.page,
            'per_page': paginated.per_page,
            'pages': paginated.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@checkout_bp.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        order.status = data['status']
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500