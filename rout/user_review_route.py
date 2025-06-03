from controller.user_reviews import product_review


def  register_product_review_routes(app):
    app.route('/product_review', methods=['POST'])(product_review)