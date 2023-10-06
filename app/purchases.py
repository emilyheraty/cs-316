from flask import render_template
from flask_login import current_user


from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('purchases', __name__)

@bp.route('/purchases', methods = ['GET'])
def purchases():
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(
            current_user.id)
    else:
        purchases = None
    return render_template('purchases.html',
                            purchase_history=purchases)