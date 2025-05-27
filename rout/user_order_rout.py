from controller.user_orders import create_order
from controller.user_orders import change_order_status
from controller.user_orders import update_order
from controller.user_orders import get_user_orders
from controller.user_orders import delete_order
from controller.user_orders import get_specific_order

def  register_create_order_routes(app):
    app.route('/add_user_order', methods=['POST'])(create_order)

def  register_change_order_status_routes(app):
    app.route('/change_order_status', methods=['POST'])(change_order_status)

def register_update_order_routes(app):
    app.route('/update_user_order', methods=['POST'])(update_order)

def register_get_user_orders_routes(app):
    app.route('/get_user_orders', methods=['POST'])(get_user_orders)

def register_delete_order_routes(app):
    app.route('/delete_user_order', methods=['POST'])(delete_order)

def register_get_specific_order_routes(app):
    app.route('/get_specific_order', methods=['POST'])(get_specific_order)

