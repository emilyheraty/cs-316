from flask_login import current_user
from flask import Blueprint, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp
from .models.cart import Cart
from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory, Listing
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime

bp = Blueprint('cart_bp', __name__)


@bp.route('/cart')
def showCart():
    if current_user.is_authenticated:
        lineitems = Cart.getCartByBuyerId(current_user.id)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        lineitems = []
        isseller=0

    per_page = 8
    # get all available products for sale:
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    lineitems_partial = Cart.getPartialCartByBuyerId(current_user.id, per_page, offset)
    search = request.args.get('q')
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(lineitems), search=search, record_name='lineitems')
    # render the cart_page template. 
    return render_template('cart_page.html', items=lineitems_partial, pagination=pagination, isseller=isseller)

@bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
def addItemToCart(product_id):
    product = Product.get(product_id)
    quantity=1
    if current_user.is_authenticated:
        Cart.addToCart(current_user.id, 0, product.id, quantity, product.price)
    else:
        redirect('/login')
    # Should take you to order page to determine quantity, and maybe other options?

    
    #bid, sid, pid, quant, price
    return redirect('/')

@bp.route('/cart/submit', methods=['GET', 'POST'])
def submitCart():
    if current_user.is_authenticated:
        lineitems = Cart.getCartByBuyerId(current_user.id)
    else:
        redirect('/login')

    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    for purch in lineitems:
        # if user can afford it
        amount = round(purch.quantity * purch.price, 2)
        Purchase.submitPurchase(purch.buyer_id, 
                                purch.product_id, 
                                str(time),
                                amount, 
                                purch.quantity, 
                                0
        )
    #uid, pid, time, sid, amount, quant, status
    
    return redirect('/purchases')

@bp.route('/detailed_product/<string:product_name>', methods=['GET', 'POST'])
def detailedOrder(product_name):
    listings = Listing.get_listings_by_product_name(product_name)
    for listing in listings:
        print(listing.sfirstname)
    prod = Product.get_product_by_name(product_name)
    desc = prod.description
    p = prod.price
    return render_template('detailed_product.html', items=listings, description = desc, price = p, product_name=product_name)
