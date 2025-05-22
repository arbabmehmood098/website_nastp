from controller.login_controller import login

def register_login_routes(app):
    app.route('/login', methods=['POST'])(login)