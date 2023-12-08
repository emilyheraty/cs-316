from flask import render_template, redirect, Blueprint, request
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from .models.order import Order
from .models.purchase import Purchase
from .models.inventory import Inventory
from flask_paginate import Pagination, get_page_parameter
from flask import Blueprint

bp = Blueprint('purchases', __name__)


@bp.route('/purchases', methods = ['GET'])
def purchases():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(
            current_user.id)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        purchases = None
        isseller = 0
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total = len(purchases)
    pagination_purchases = purchases[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total)
    return render_template('purchases.html',
                            purchase_history=pagination_purchases, pagination=pagination, isseller=isseller)

@bp.route('/orders/', methods = ['GET'])
def orders():
    if current_user.is_authenticated and Inventory.isSeller(current_user.id)[0][0]: # isSeller
        lineitems = Order.getOrdersBySellerId(current_user.id)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        lineitems = []
        isseller=0
    per_page = 8
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    lineitems_partial = Order.getPartialOrdersBySellerId(current_user.id, per_page, offset)
    search = request.args.get('q')
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(lineitems), search=search, record_name='lineitems')
    return render_template('orders.html', items=lineitems_partial, pagination=pagination, isseller=isseller)
