from flask import render_template
from flask_login import current_user


from .models.purchase import Purchase
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('purchases', __name__)

@bp.route('/purchases', methods = ['GET'])
def purchases():
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(
            current_user.id)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        purchases = None
        isseller = 0
    return render_template('purchases.html',
                            purchase_history=purchases, isseller = isseller)