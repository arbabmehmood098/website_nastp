from controller.user_orders import create_order
from controller.user_orders import delete_order

def  register_create_order_routes(app):
    app.route('/add_user_products', methods=['POST'])(create_order)

def  register_delete_order_routes(app):
    app.route('/delete_user_products', methods=['POST'])(delete_order)