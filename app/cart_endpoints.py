from flask_login import current_user
from flask import jsonify, Blueprint
from .models.cart import Cart
from .models.product import Product
bp = Blueprint('index', __name__)


@bp.route('/cart')
def index():
    # get all available products for sale:
    # find the products current user has bought:
    if current_user.is_authenticated:
        products = Cart.getCartByBuyerId(current_user.id)
        # need to get product name by id for each item. 
    else:
        products = None
    # render the page by adding information to the index.html file
    return render_template('cart_page.html', items=products)
