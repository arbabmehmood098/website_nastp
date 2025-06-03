import uuid
from datetime import datetime
from flask import request, jsonify
from firebase_config import auth, db


def product_review():
    # Authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required"}), 401

    try:
        token = auth_header.split('Bearer ')[1].strip()
        data = request.get_json()

        # Validate required fields
        required_fields = ['content', 'rating', 'product_id']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

        # Verify token and get user info
        user = auth.get_account_info(token)
        user_uid = user['users'][0]['localId']
        user_email = user['users'][0]['email']
        username = user_email.split('@')[0]  # Using email prefix as username

        # Validate rating
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        # Create review data (without review_id)
        review_data = {
            "user_uid": user_uid,
            "username": username,
            "content": data['content'],
            "rating": rating,
            "likes": 0,
            "liked_by": {},
            "avatar": "https://placehold.com / 72x70",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

        # Get current reviews array
        product_ref = db.child("siberkoza").child("company").child("products").child(data['product_id'])
        product_data = product_ref.get().val() or {}

        # Initialize reviews array if it doesn't exist
        if 'reviews' not in product_data:
            product_data['reviews'] = []

        # Add new review to array
        product_data['reviews'].append(review_data)

        # Update the product with new reviews array
        db.child("siberkoza").child("company").child("products").child(data['product_id']).update({"reviews": product_data['reviews']})

        return jsonify({
            "message": "Review added successfully",
            "review": review_data
        }), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create review: {str(e)}"}), 500