from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify
from flask import redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.inventory import Inventory
# from .models.inventory import addToInventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)

class AddProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add')

@bp.route('/inventory/<int:seller_id>')
def inventory(seller_id):
    # get all available products for sale:
    items = Inventory.getInventory(seller_id)
    seller_info = Inventory.getSellerInfo(seller_id)
    # return jsonify([item.__dict__ for item in items])
    return render_template('inventory.html',
                           id=seller_info[0][0],
                           name=seller_info[0][1],
                           inv=items)

@bp.route('/inventory/<int:seller_id>/add', methods = ['GET', 'POST'])
def add_products(seller_id):
    seller_info = Inventory.getSellerInfo(seller_id)
    if current_user.is_authenticated:
        items = Inventory.getInventory(current_user.id)
        form = AddProduct()
        if form.validate_on_submit():
            pname = form.product_name.data
            amt = form.quantity.data
            Inventory.addToInventory(seller_id, pname, amt)
            flash('Added new product!')
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('inventory-addproduct.html', form=form)
