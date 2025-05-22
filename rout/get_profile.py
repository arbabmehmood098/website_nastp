from controller.get_profile_controller import get_profile

def register_get_profile_routes(app):
    app.route('/profile', methods=['GET'])(get_profile)