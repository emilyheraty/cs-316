from flask_login import current_user
from flask import Blueprint, render_template
from .models.cart import Cart
bp = Blueprint('cart_bp', __name__)


@bp.route('/cart')
def showCart():
    # get all available products for sale:
    # find the products current user has bought:
    if current_user.is_authenticated:
        products = Cart.getCartByBuyerId(current_user.id)
        for cart in products:
            print(cart.prod_name)
        # need to get product name by id for each item. 
    else:
        products = None
    # render the page by adding information to the index.html file
    return render_template('cart_page.html', items=products)
