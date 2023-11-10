from flask import render_template, Blueprint, request
from flask_login import current_user
from flask_paginate import Pagination, get_page_args


from .models.purchase import Purchase
from .models.inventory import Inventory

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