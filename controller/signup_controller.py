from flask import request, jsonify
from firebase_config import auth, db
import json

def signup():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    try:
        # Create user in Firebase Authentication
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user['localId']  # Get unique Firebase user ID

        # Store user data in Firebase Realtime Database under siberkoza/users/<user_id>
        user_data = {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        db.child("siberkoza").child("users").child(user_id).set(user_data)

        # Retrieve saved data from Firebase
        saved_user = db.child("siberkoza").child("users").child(user_id).get().val()

        return jsonify({
            "message": "User created successfully.",
            "user_data": saved_user
        }), 201

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']

            if error_message == "EMAIL_EXISTS":
                return jsonify({"error": "User already exists."}), 400
            else:
                return jsonify({"error": error_message}), 400

        except Exception:
            return jsonify({"error": "An unexpected error occurred."}), 400