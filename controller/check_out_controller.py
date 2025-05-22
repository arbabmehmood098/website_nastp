from flask import request, jsonify
from firebase_config import admin_auth, db

def checkout():
    # Get the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        print(f"Missing or invalid Authorization header: {auth_header}")
        return jsonify({"error": "Authorization token required"}), 401

    # Extract the ID token
    try:
        id_token = auth_header.split('Bearer ')[1].strip()
        if len(id_token.split('.')) != 3:
            print(f"Invalid token format: {id_token}")
            return jsonify({"error": "Invalid token format"}), 401
    except IndexError:
        print(f"Malformed Authorization header: {auth_header}")
        return jsonify({"error": "Malformed Authorization header"}), 401

    # Verify the ID token using Firebase Admin SDK
    try:
        decoded_token = admin_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return jsonify({"error": f"Invalid or expired token: {str(e)}"}), 401

    # Get the request data
    data = request.get_json()
    provided_address = data.get('address')

    # Validate that an address is provided
    if not provided_address:
        return jsonify({"error": "Address is required"}), 400

    # Update the address under users/<user_id>/address
    try:
        db.child("siberkoza").child("users").child(user_id).child("address").set(provided_address)
        return jsonify({
            "message": "Address updated successfully during checkout",
            "user_id": user_id,
            "address": provided_address
        }), 200
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": f"Failed to update address: {str(e)}"}), 400