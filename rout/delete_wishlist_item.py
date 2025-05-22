from controller.delete_wishlist_item_controller import delete_wishlist_item

def register_delete_wishlist_routes(app):
    app.route('/wishlist/<wishlist_name>/items/<item_id>', methods=['POST'])(delete_wishlist_item)