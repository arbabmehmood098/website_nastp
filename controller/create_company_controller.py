from flask import request, jsonify
from firebase_config import auth, db, admin_auth
import json

def company_signup():
    data = request.get_json()

    # Required fields
    company_name = data.get('company_name')
    email = data.get('email')
    password = data.get('password')

    if not company_name or not email or not password:
        return jsonify({"error": "Company name, email, and password are required."}), 400

    try:
        # Check if company already exists
        existing_company = db.child("siberkoza").child("company").get().val()
        if existing_company:
            return jsonify({"error": "Only one company can be registered."}), 400

        # Create company account in Firebase Auth
        user = auth.create_user_with_email_and_password(email, password)
        company_auth_id = user['localId']

        # Company data structure
        company_data = {
            "company_name": company_name,
            "email": email,
            "auth_id": company_auth_id,
        }

        # Save to database
        db.child("siberkoza").child("company").set(company_data)

        return jsonify({
            "message": "Company registered successfully.",
            "company_data": {
                "company_name": company_name,
                "email": email
            },
            "auth_id": company_auth_id
        }), 201

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']
            if error_message == "EMAIL_EXISTS":
                return jsonify({"error": "Email already in use."}), 400
            return jsonify({"error": error_message}), 400
        except:
            return jsonify({"error": "An unexpected error occurred during registration."}), 500

def company_login():
    data = request.get_json()

    # Required fields
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        # Authenticate with Firebase Auth
        user = auth.sign_in_with_email_and_password(email, password)
        company_auth_id = user['localId']

        # Get company data from database
        company_ref = db.child("siberkoza").child("company")
        company_data = company_ref.get().val()

        # Verify the company exists and matches the authenticated user
        if not company_data:
            return jsonify({"error": "Company not found. Please register first."}), 404

        if company_data.get('auth_id') != company_auth_id:
            return jsonify({
                "error": "Authentication mismatch.",
                "details": {
                    "database_auth_id": company_data.get('auth_id'),
                    "current_auth_id": company_auth_id
                }
            }), 403

        response_data = {
            "message": "Login successful",
            "company": {
                "company_name": company_data.get('company_name'),
                "email": company_data.get('email')

            },
            "auth": {
                "idToken": user['idToken'],
                "refreshToken": user['refreshToken'],
                "expiresIn": user['expiresIn'],
                "localId": company_auth_id
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        error_json = e.args[1] if len(e.args) > 1 else str(e)
        try:
            error_data = json.loads(error_json)
            error_message = error_data['error']['message']
            if error_message == "INVALID_EMAIL":
                return jsonify({"error": "Invalid email address."}), 400
            elif error_message == "INVALID_PASSWORD":
                return jsonify({"error": "Invalid password."}), 400
            elif error_message == "USER_DISABLED":
                return jsonify({"error": "Account disabled."}), 403
            return jsonify({"error": error_message}), 400
        except:
            return jsonify({"error": "An unexpected error occurred during login."}), 500


def update_company_info():
    data = request.get_json()

    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header with Bearer token is required."}), 401

    token = auth_header.split('Bearer ')[1].strip()

    try:
        # Verify the token and get user ID
        user = auth.get_account_info(token)
        company_auth_id = user['users'][0]['localId']

        # Get current company data
        company_ref1 = db.child("siberkoza").child("company")
        company_data = company_ref1.get().val()


        # Verify company exists and auth_id matches
        if not company_data:
            return jsonify({"error": "Company not found. Please register first."}), 404

        # if company_data.get('auth_id') != company_auth_id:
        #     return jsonify({"error": "Unauthorized to update this company."}), 403

        # Prepare info updates (only update fields that are provided)
        info_updates = {}
        info_fields = [
            'address', 'phone', 'website', 'description',
            'logo_url', 'tax_id', 'industry', 'founding_date'
        ]

        current_info = company_data.get('info', {})


        for field in info_fields:
            if field in data:
                info_updates[field] = data[field]

            elif field in current_info:
                info_updates[field] = current_info[field]

        # Update the info in database
        db.child("siberkoza").child("company").child("info").update(info_updates)

        # Return the updated info
        return jsonify({
            "message": "Company information updated successfully.",
            "updated_info": info_updates
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
            return jsonify({"error": "An unexpected error occurred during update."}), 500