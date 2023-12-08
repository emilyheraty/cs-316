from flask import render_template
from flask_login import current_user, login_required
import datetime
from .models.feedback import Feedback
from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from flask import current_app
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        user_id = current_user.id
        is_seller = Inventory.isSeller(current_user.id)[0][0]
    else:
        purchases = []
        is_seller = False
    # render the page by adding information to the index.html file
    return render_template('index.html', avail_products=products, purchase_history=purchases, isseller=is_seller)

