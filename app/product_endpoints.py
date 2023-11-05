from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('product_bp', __name__)


@bp.route('/product/<int:k>')
def top_k_products(k):
    products = Product.get_k_products(k)
    # get all available products for sale:
    #products = Product.get_all(True)
    # find the products current user has bought:

    # render the page by adding information to the index.html file
    return render_template('temp_products.html',
                           items=products
                        )