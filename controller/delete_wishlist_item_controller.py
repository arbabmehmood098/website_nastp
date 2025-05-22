from flask import request, jsonify
from firebase_config import admin_auth, db

def delete_wishlist_item(wishlist_name, item_id):
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

    # Check if the item exists
    try:
        item = db.child("siberkoza").child("users").child(user_id).child("wishlist").child(matching_wishlist_id).child("items").child(item_id).get().val()
        if not item:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        print(f"Item lookup error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Failed to validate item: {str(e)}"}), 400

    # Delete the item
    try:
        db.child("siberkoza").child("users").child(user_id).child("wishlist").child(matching_wishlist_id).child("items").child(item_id).remove()
        return jsonify({
            "message": "Item deleted from wishlist successfully",
            "item_id": item_id
        }), 200
    except Exception as e:
        print(f"Database error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Failed to delete item: {str(e)}"}), 400