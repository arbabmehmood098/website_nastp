from controller.create_wishlist_controller import create_wishlist

def register_create_wishlist_routes(app):
    app.route('/wishlist/create', methods=['POST'])(create_wishlist)