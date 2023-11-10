from flask_login import current_user
from flask import Blueprint, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp
from .models.cart import Cart
from .models.product import Product

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

@bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def addItemToCart(product_id):
    product = Product.get(product_id)
    quantity=1
    # Should take you to order page to determine quantity, and maybe other options?
    Cart.addToCart(current_user.id, 0, product.id, quantity, product.price)
    #bid, sid, pid, quant, price
    return redirect('/')