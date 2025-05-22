from firebase_config import auth, db, admin_auth
import uuid
from datetime import datetime
from flask import jsonify, request

def create_order():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required fields
        required_fields = ['user_id', 'products', 'total_amount']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        # Verify token and get user ID (assuming this is a company token)
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Create order data
        order_data = {
            "order_id": str(uuid.uuid4()),
            "company_auth_id": company_auth_id,
            "user_id": data['user_id'],
            "products": data['products'],  # List of product IDs with quantities
            "total_amount": float(data['total_amount']),
            "status": data.get('status', 'pending'),
            "shipping_address": data.get('shipping_address', {}),
            "billing_address": data.get('billing_address', {}),
            "payment_method": data.get('payment_method', ''),
            "payment_status": data.get('payment_status', 'unpaid'),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "notes": data.get('notes', '')
        }

        # Add to database
        # db.child("siberkoza").child("users").child("user_id").child(order_data['order_id']).child("orders").set(order_data)
        db.child("siberkoza").child("users").child(data['user_id']).child("orders").set(order_data)
        return jsonify({
            "message": "Order created successfully",
            "order": order_data
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create order: {str(e)}"}), 500


def delete_order():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required fields
        if 'order_id' not in data or 'user_id' not in data:
            return jsonify({"error": "Order ID and User ID are required"}), 400

        # Verify token and get company ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Debugging: Print the reference path
        order_path = f"siberkoza/users/{data['user_id']}/orders/{data['order_id']}"
        print(f"Attempting to access order at path: {order_path}")

        # Get order reference
        order_ref = db.child("siberkoza").child("users").child(data['user_id']).child("orders").child(data['order_id'])
        order_data = order_ref.get().val()

        # Debugging: Print what was found
        print(f"Order data found: {order_data}")

        # Check if order exists
        if not order_data:
            # Additional check - verify user exists
            user_ref = db.child("siberkoza").child("users").child(data['user_id']).get().val()
            if not user_ref:
                return jsonify({"error": "User not found"}), 404
            return jsonify({"error": "Order not found for this user"}), 404

        # Check authorization
        if order_data.get('company_auth_id') != company_auth_id:
            return jsonify({"error": "Unauthorized to delete this order"}), 403

        # Delete the order
        order_ref.remove()
        print(f"Order {data['order_id']} successfully deleted")

        return jsonify({
            "message": "Order deleted successfully",
            "order_id": data['order_id']
        }), 200

    except Exception as e:
        print(f"Error deleting order: {str(e)}")
        return jsonify({"error": f"Failed to delete order: {str(e)}"}), 500