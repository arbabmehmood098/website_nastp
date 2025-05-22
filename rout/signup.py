from controller.signup_controller import signup

def register_signup_routes(app):
    app.route('/signup', methods=['POST'])(signup)