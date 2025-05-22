from flask import request, jsonify
from firebase_config import admin_auth, db
import json

def update_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', "")
    data = request.get_json()

    if not token:
        return jsonify({"error": "Authorization token is required."}), 400

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')

    if not name or not email:
        return jsonify({"error": "Name and email are required."}), 400

    try:
        # Verify Firebase ID token using Firebase Admin SDK
        decoded_token = admin_auth.verify_id_token(token)
        user_id = decoded_token['uid']

        # Prepare profile data
        profile_data = {
            "name": name,
            "email": email,
            "phone": phone or "",
            "address": address or ""
        }

        # Store profile data in Firebase Realtime Database using Pyrebase
        db.child("siberkoza").child("users").child(user_id).child("profile").set(profile_data)

        # Retrieve saved data from Firebase
        saved_profile = db.child("users").child(user_id).child("profile").get().val()

        return jsonify({
            "message": "Profile updated successfully.",
            "profile_data": saved_profile
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