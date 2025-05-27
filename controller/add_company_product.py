from firebase_config import auth, db, admin_auth
from flask import jsonify, request
from datetime import datetime
import uuid
import json

def add_product():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'price', 'category_id', 'description', 'collection']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        # Verify token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Create product data with new attributes
        product_data = {
            "id": str(uuid.uuid4()),
            "company_auth_id": company_auth_id,
            "name": data['name'],
            "price": float(data['price']),
            "originalPrice": float(data.get('originalPrice', data['price'])),
            "rating": float(data.get('rating', 0)),
            "badge": data.get('badge', ""),
            "discount": data.get('discount', ""),
            "image": data.get('image', ""),
            "images": data.get('images', []),
            "description": data['description'],
            "category_id": data['category_id'],
            "collection": data['collection'],
            "reviewCount": int(data.get('reviewCount', 0)),
            "review": data.get('review', {}),
            "color": data.get('color', []),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "is_active": bool(data.get('is_active', True))
        }

        # Add to database
        db.child("siberkoza").child("company").child("products").child(product_data['id']).set(product_data)

        return jsonify({
            "message": "Product added successfully",
            "product": product_data
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to add product: {str(e)}"}), 500

def get_products():
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required."}), 401

    token = auth_header.split('Bearer ')[1].strip()

    try:
        # Verify the token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Get all products
        products_ref = db.child("siberkoza").child("company").child("products")
        all_products = products_ref.get().val() or {}

        # Filter products belonging to this company
        company_products = {
            pid: product for pid, product in all_products.items()
            if product.get('company_auth_id') == company_auth_id
        }

        if not company_products:
            return jsonify({
                "message": "No products found for this company",
                "products": {}
            }), 200

        return jsonify({
            "message": "Products retrieved successfully",
            "products": company_products
        }), 200

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']
            if error_message == "INVALID_ID_TOKEN":
                return jsonify({"error": "Invalid or expired token."}), 401
            return jsonify({"error": error_message}), 400
        except:
            return jsonify({"error": "An unexpected error occurred while fetching products."}), 500

def get_product():
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required."}), 401

    token = auth_header.split('Bearer ')[1].strip()

    # Parse JSON body
    data = request.get_json()
    if not data or 'product_id' not in data:
        return jsonify({"error": "Product ID is required in the request body."}), 400

    product_id = data['product_id']

    try:
        # Verify the token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Get the specific product
        product = db.child("siberkoza").child("company").child("products").child(product_id).get().val()

        if not product:
            return jsonify({"error": "Product not found."}), 404

        # Check if product belongs to the company
        if product.get('company_auth_id') != company_auth_id:
            return jsonify({"error": "Unauthorized to view this product."}), 403

        return jsonify({
            "message": "Product retrieved successfully",
            "product": product
        }), 200

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']
            if error_message == "INVALID_ID_TOKEN":
                return jsonify({"error": "Invalid or expired token."}), 401
            return jsonify({"error": error_message}), 400
        except:
            return jsonify({"error": "An unexpected error occurred while fetching the product."}), 500

def update_product():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required fields
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        if not data.get('updates'):
            return jsonify({"error": "No updates provided"}), 400

        # Verify token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Product reference
        product_ref = db.child("siberkoza").child("company").child("products").child(product_id)
        product_data = product_ref.get().val()

        # Check if product exists
        if not product_data:
            return jsonify({"error": "Product not found"}), 404

        # Check if product belongs to the company
        if product_data.get('company_auth_id') != company_auth_id:
            return jsonify({"error": "Unauthorized to update this product"}), 403

        # Prepare updates
        updates = data['updates']
        protected_fields = ['id', 'company_auth_id', 'created_at']

        for field in protected_fields:
            if field in updates:
                del updates[field]

        # Type conversions for specific fields
        numeric_fields = ['price', 'originalPrice', 'rating']
        for field in numeric_fields:
            if field in updates:
                updates[field] = float(updates[field])

        if 'reviewCount' in updates:
            updates['reviewCount'] = int(updates['reviewCount'])

        # Add updated_at timestamp
        updates['updated_at'] = datetime.utcnow().isoformat() + "Z"

        # Update product
        product_ref.update(updates)

        # Fetch updated product
        updated_product = product_ref.get().val()

        return jsonify({
            "message": "Product updated successfully",
            "product_id": product_id,
            "updated_product": updated_product
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update product: {str(e)}"}), 500

def delete_product():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required field
        if 'product_id' not in data:
            return jsonify({"error": "Product ID is required"}), 400

        # Verify token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        product_ref = db.child("siberkoza").child("company").child("products").child(data['product_id'])
        product_data = product_ref.get().val()

        # Check if product exists and belongs to this company
        if not product_data:
            return jsonify({"error": "Product not found"}), 404

        if product_data.get('company_auth_id') != company_auth_id:
            return jsonify({"error": "Unauthorized to delete this product"}), 403

        # Delete product
        product_ref.remove()

        return jsonify({
            "message": "Product deleted successfully",
            "product_id": data['product_id']
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete product: {str(e)}"}), 500