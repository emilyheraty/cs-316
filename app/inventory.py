from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify

from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)


@bp.route('/inventory/<int:seller_id>')
def inventory(seller_id):
    # get all available products for sale:
    items = Inventory.getInventory(seller_id)
    seller_name = Inventory.getSellerName(seller_id)
    # return jsonify([item.__dict__ for item in items])
    return render_template('inventory.html',
                           name=seller_name[0][0],
                           inv=items)

    # find the products current user has bought:
    # if current_user.is_authenticated:
    #     purchases = Purchase.get_all_by_uid_since(
    #         current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    # else:
    #     purchases = None
    # render the page by adding information to the index.html file
    # return render_template('index.html',
    #                        avail_products=products,
    #                        purchase_history=purchases)