from controller.get_wishlist_controller import get_wishlist

def register_get_wishlist_routes(app):
    app.route('/wishlist/<wishlist_name>', methods=['GET'])(get_wishlist)