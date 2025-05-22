from controller.add_wishlist_item_controller import add_item_to_wishlist

def  register_add_wishlist_item_routes(app):
    app.route('/wishlist/<wishlist_name>/items', methods=['POST'])(add_item_to_wishlist)