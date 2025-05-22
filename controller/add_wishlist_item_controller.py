from flask import request, jsonify
from firebase_config import admin_auth, db
import time

def add_item_to_wishlist(wishlist_name):
    # Get the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print(f"Missing or invalid Authorization header: {auth_header}")  # Log for debugging
        return jsonify({"error": "Authorization token required"}), 401

    # Extract the ID token
    try:
        id_token = auth_header.split('Bearer ')[1].strip()
        # Validate token format (3 segments: header.payload.signature)
        if len(id_token.split('.')) != 3:
            print(f"Invalid token format: {id_token}")  # Log for debugging
            return jsonify({"error": "Invalid token format"}), 401
    except IndexError:
        print(f"Malformed Authorization header: {auth_header}")  # Log for debugging
        return jsonify({"error": "Malformed Authorization header"}), 401

    # Verify the ID token using Firebase Admin SDK
    try:
        decoded_token = admin_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
    except Exception as e:
        print(f"Token verification error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Invalid or expired token: {str(e)}"}), 401

    # Find the wishlist by name
    try:
        wishlists = db.child("siberkoza").child("users").child(user_id).child("wishlist").get().val()
        if not wishlists:
            return jsonify({"error": "Wishlist not found"}), 404

        matching_wishlist_id = None
        match_count = 0
        for wishlist_id, wishlist_data in wishlists.items():
            if wishlist_data.get('name') == wishlist_name:
                matching_wishlist_id = wishlist_id
                match_count += 1

        if match_count == 0:
            return jsonify({"error": "Wishlist not found"}), 404
        if match_count > 1:
            return jsonify({"error": "Multiple wishlists with the same name found"}), 400

    except Exception as e:
        print(f"Wishlist lookup error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Failed to validate wishlist: {str(e)}"}), 400

    # Get item data from the request body
    data = request.get_json()
    product_name = data.get('product_name')
    price = data.get('price')
    url = data.get('url')

    if not product_name:
        return jsonify({"error": "Product name is required"}), 400

    try:
        # Create item data
        item_data = {
            "product_name": product_name,
            "added_at": time.time()  # Store timestamp in seconds
        }
        if price is not None:
            item_data["price"] = price
        if url:
            item_data["url"] = url

        # Save item under users/<user_id>/wishlist/<wishlist_id>/items/<item_id>
        item_ref = db.child("siberkoza").child("users").child(user_id).child("wishlist").child(matching_wishlist_id).child("items").push(item_data)
        item_id = item_ref['name']  # Get the generated item ID

        # Retrieve the saved item
        saved_item = db.child("siberkoza").child("users").child(user_id).child("wishlist").child(matching_wishlist_id).child("items").child(item_id).get().val()

        return jsonify({
            "message": "Item added to wishlist successfully",
            "item_id": item_id,
            "item_data": saved_item
        }), 201

    except Exception as e:
        print(f"Database error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Failed to add item to wishlist: {str(e)}"}), 400