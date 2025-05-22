from flask import request, jsonify
from firebase_config import admin_auth, db
import time

def create_wishlist():
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

    # Get the wishlist name from the request body
    data = request.get_json()
    wishlist_name = data.get('name')

    if not wishlist_name:
        return jsonify({"error": "Wishlist name is required"}), 400

    try:
        # Create wishlist data
        wishlist_data = {
            "name": wishlist_name,
            "created_at": time.time()  # Store timestamp in seconds
        }

        # Save wishlist under users/<user_id>/wishlist/<wishlist_id> using Pyrebase
        wishlist_ref = db.child("siberkoza").child("users").child(user_id).child("wishlist").push(wishlist_data)
        wishlist_id = wishlist_ref['name']  # Get the generated wishlist ID

        # Retrieve the saved wishlist
        saved_wishlist = db.child("siberkoza").child("users").child(user_id).child("wishlist").child(wishlist_id).get().val()

        return jsonify({
            "message": "Wishlist created successfully",
            "wishlist_id": wishlist_id,
            "wishlist_data": saved_wishlist
        }), 201

    except Exception as e:
        print(f"Database error: {str(e)}")  # Log for debugging
        return jsonify({"error": f"Failed to create wishlist: {str(e)}"}), 400