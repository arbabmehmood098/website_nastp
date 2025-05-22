from controller.add_company_product import get_products
from controller.add_company_product import update_product
from controller.add_company_product import add_product
from controller.add_company_product import delete_product
from controller.add_company_product import get_product

def  register_add_product_routes(app):
    app.route('/add_company_products', methods=['POST'])(add_product)

def  register_get_products_routes(app):
    app.route('/get_company_products', methods=['POST'])(get_products)

def  register_update_product_routes(app):
    app.route('/update_company_product', methods=['PUT'])(update_product)

def  register_delete_product_routes(app):
    app.route('/delete_company_products', methods=['POST'])(delete_product)

def  register_get_product_routes(app):
    app.route('/get_company_product', methods=['POST'])(get_product)