from flask_login import current_user
from flask import Blueprint, render_template, redirect
from .models.cart import Cart
bp = Blueprint('cart_bp', __name__)


@bp.route('/cart')
def showCart():
    # find items in cart of current user. 
    if current_user.is_authenticated:
        products = Cart.getCartByBuyerId(current_user.id)
    else:
        products = []
    # render the cart_page template. 
    return render_template('cart_page.html', items=products)

@bp.route('/cart/add/<int:product_id>/<int:quantity>', methods=['POST'])
def addToCart():

    return redirect('/')
