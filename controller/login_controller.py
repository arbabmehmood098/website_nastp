from flask import request, jsonify
from firebase_config import auth
import json

def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        user = auth.sign_in_with_email_and_password(email, password)

        return jsonify({
            "message": "Login successful.",
            "email": email,
            "idToken": user['idToken']
        }), 200

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']

            if error_message == "EMAIL_NOT_FOUND":
                return jsonify({"error": "Email not found. Please register first."}), 404
            elif error_message == "INVALID_PASSWORD":
                return jsonify({"error": "Invalid password. Please try again."}), 401
            elif error_message == "USER_DISABLED":
                return jsonify({"error": "This user account has been disabled."}), 403
            else:
                return jsonify({"error": error_message}), 400

        except Exception:
            return jsonify({"error": "An unknown error occurred."}), 500