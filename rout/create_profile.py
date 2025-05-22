from controller.create_profile_controller import update_profile

def register_update_profile_routes(app):
    app.route('/profile', methods=['POST'])(update_profile)