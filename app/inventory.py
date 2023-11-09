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
from flask_paginate import Pagination, get_page_parameter

from .models.inventory import Inventory


from flask import Blueprint
bp = Blueprint('inventory', __name__)

class AddProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add')

class DeleteProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    submit = SubmitField('Delete')

class UpdateQuantity(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    new_quantity = IntegerField('New Quantity', validators=[DataRequired()])
    submit = SubmitField('Update')

@bp.route('/inventory/<int:seller_id>')
def inventory(seller_id):
    # get all available products for sale:
    items = Inventory.getInventory(seller_id)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    search = False
    q = request.args.get('q')
    if q:
        search = True
    pagination = Pagination(page=page, total=len(items), search=search, record_name='inventory items')
    seller_info = Inventory.getSellerInfo(seller_id)
    # return jsonify([item.__dict__ for item in items])
    return render_template('inventory.html',
                           id=seller_info[0][0],
                           name=seller_info[0][1],
                           inv=items,
                           isseller=1,
                           pagination=pagination)

@bp.route('/inventory/<int:seller_id>/add', methods = ['GET', 'POST'])
def add_products(seller_id):
    seller_info = Inventory.getSellerInfo(seller_id)
    if current_user.is_authenticated:
        items = Inventory.getInventory(current_user.id)
        form = AddProduct()
        if form.validate_on_submit():
            pname = form.product_name.data
            amt = form.quantity.data
            result = Inventory.addToInventory(seller_id, pname, amt)
            if result == 0:
                return render_template('inventory-addproduct.html', form=form,isseller=1, error=1)
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('inventory-addproduct.html', form=form, isseller=1, error=0)

@bp.route('/inventory/<int:seller_id>/delete', methods = ['GET', 'POST'])
def delete_products(seller_id):
    seller_info = Inventory.getSellerInfo(seller_id)
    if current_user.is_authenticated:
        items = Inventory.getInventory(current_user.id)
        form = DeleteProduct()
        if form.validate_on_submit():
            pname = form.product_name.data
            result = Inventory.removeProductFromInventory(seller_id, pname)
            if result == 0:
                return render_template('inventory-deleteproduct.html', form=form,isseller=1, error=1)
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('inventory-deleteproduct.html', form=form, isseller=1, error=0)

@bp.route('/inventory/<int:seller_id>/updatequantity', methods = ['GET', 'POST'])
def update_products(seller_id):
    seller_info = Inventory.getSellerInfo(seller_id)
    if current_user.is_authenticated:
        items = Inventory.getInventory(current_user.id)
        form = UpdateQuantity()
        if form.validate_on_submit():
            pname = form.product_name.data
            amt = form.new_quantity.data
            result = Inventory.updateProductQuantity(seller_id, pname, amt)
            print(result)
            if result == 0:
                return render_template('inventory-updateproduct.html', form=form,isseller=1, error=1)
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('inventory-updateproduct.html', form=form, isseller=1, error=0)