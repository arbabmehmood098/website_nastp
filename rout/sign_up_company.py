from controller.create_company_controller import company_signup
from controller.create_company_controller import company_login
from controller.create_company_controller import update_company_info


def register_company_signup_routes(app):
    app.route('/company_signup', methods=['POST'])(company_signup)


def register_company_login_routes(app):
    app.route('/company_login', methods=['POST'])(company_login)

def register_update_company_info_routes(app):
    app.route('/update_company_info', methods=['POST'])(update_company_info)
