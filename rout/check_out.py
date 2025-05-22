from controller.check_out_controller import checkout

def  register_check_out_routes(app):
    app.route('/checkout', methods=['POST'])(checkout)