from flask import request, jsonify
from firebase_config import admin_auth, db
import json

def get_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({"error": "Authorization token is required."}), 400

    try:
        # Verify Firebase ID token using Firebase Admin SDK
        decoded_token = admin_auth.verify_id_token(token)
        user_id = decoded_token['uid']

        # Retrieve profile data from Firebase Realtime Database using Pyrebase
        profile_data = db.child("siberkoza").child("users").child(user_id).child("profile").get().val()

        if not profile_data:
            return jsonify({"error": "Profile not found."}), 404

        return jsonify({
            "message": "Profile retrieved successfully.",
            "profile_data": profile_data
        }), 200

    except admin_auth.InvalidIdTokenError:
        return jsonify({"error": "Invalid or expired token."}), 401
    except admin_auth.ExpiredIdTokenError:
        return jsonify({"error": "Token has expired."}), 401
    except Exception as e:
        error_json = str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']
            return jsonify({"error": error_message}), 400
        except Exception:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 400