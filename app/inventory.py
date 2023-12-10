from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify
from flask import redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SearchField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_paginate import Pagination, get_page_parameter

from .models.inventory import Inventory
from .models.product import Product


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

class Search(FlaskForm):
    search_input = SearchField('Product Name', validators=[DataRequired()])
    submit = SubmitField('Search')

class CreateNewProduct(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_description = StringField('Product Description', validators=[DataRequired()])
    product_category = StringField('Category', validators=[DataRequired()])
    product_price = DecimalField('Price', validators=[DataRequired()])
    add_to_inventory = BooleanField('Check to Add to Inventory')
    quantity = IntegerField('Quantity to Add to Inventory')
    submit = SubmitField('Create')

@bp.route('/inventory/<int:seller_id>', methods = ['GET', 'POST'])
def inventory(seller_id):
    # get all available products for sale:
    items = Inventory.getInventory(seller_id)
    per_page = 10
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    items_partial = Inventory.getPartialInventory(seller_id, per_page, offset)
    search = False
    q = request.args.get('q')
    if q:
        search = True
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(items), search=search, record_name='items')
    seller_info = Inventory.getSellerInfo(seller_id)
    isseller = 0

    # make search box
    form_search = Search()
    form_uq = UpdateQuantity()
    form_dp = DeleteProduct()
    if form_search.validate_on_submit():
        search_str = form_search.search_input.data
        result = Inventory.getInventoryProducts(search_str, per_page, offset, seller_id)
        if len(result) == 0:
            return render_template('inventory.html',
                            id=seller_info[0][0],
                            name=seller_info[0][1],
                            inv=items_partial,
                            isseller=isseller,
                            pagination=pagination,
                            form_uq=form_uq,
                            form_dp=form_dp,
                            form_search=form_search,
                            err_message="No search results found")
        else:
            return render_template('inventory.html',
                            id=seller_info[0][0],
                            name=seller_info[0][1],
                            inv=result,
                            isseller=isseller,
                            pagination=pagination,
                            form_uq=form_uq,
                            form_dp=form_dp,
                            form_search=form_search,
                            err_message=0)
    if current_user.is_authenticated:
        if current_user.id == seller_info[0][0]:
            isseller = 1
            if form_uq.validate_on_submit():
                pname = form_uq.product_name.data
                amt = form_uq.new_quantity.data
                result = Inventory.updateProductQuantity(seller_id, pname, amt)
                if result == 0:
                    return render_template('inventory.html',
                            id=seller_info[0][0],
                            name=seller_info[0][1],
                            inv=items_partial,
                            isseller=isseller,
                            pagination=pagination,
                            form_uq=form_uq,
                            form_dp=form_dp,
                            form_search=form_search,
                            err_message="error: could not update quantity")
                return redirect(url_for('inventory.inventory', seller_id=current_user.id))
            else:
                print(form_uq.errors)
            
            if form_dp.validate_on_submit():
                pname = form_dp.product_name.data
                result = Inventory.removeProductFromInventory(seller_id, pname)
                if result == 0:
                    return render_template('inventory.html',
                            id=seller_info[0][0],
                            name=seller_info[0][1],
                            inv=items_partial,
                            isseller=isseller,
                            pagination=pagination,
                            form_uq=form_uq,
                            form_dp=form_dp,
                            form_search=form_search,
                            err_message="error: could not remove product")
                return redirect(url_for('inventory.inventory', seller_id=current_user.id))
            else:
                print(form_uq.errors)
    # return jsonify([item.__dict__ for item in items])
    return render_template('inventory.html',
                           id=seller_info[0][0],
                           name=seller_info[0][1],
                           inv=items_partial,
                           isseller=isseller,
                           pagination=pagination,
                           form_uq=form_uq,
                           form_dp=form_dp,
                           form_search=form_search,
                           err_message=0)

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
            if result == 0:
                return render_template('inventory-updateproduct.html', form=form,isseller=1, error=1)
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('inventory-updateproduct.html', form=form, isseller=1, error=0)

@bp.route('/inventory/<int:seller_id>/create', methods = ['GET', 'POST'])
def create_products(seller_id):
    seller_info = Inventory.getSellerInfo(seller_id)
    if current_user.is_authenticated:
        items = Inventory.getInventory(current_user.id)
        form = CreateNewProduct()
        if form.validate_on_submit():
            name = form.product_name.data
            description = form.product_description.data
            category = form.product_category.data
            price = form.product_price.data
            cid = seller_id
            result = Product.create_new_product(description, category, cid, name, price)
            if result == 0:
                return render_template('create_product.html', form=form,isseller=1, error=1)
            add_to_inventory = form.add_to_inventory.data
            quantity = form.quantity.data
            if add_to_inventory and (quantity != 0):
                Inventory.addToInventory(seller_id, name, quantity)
            return redirect(url_for('inventory.inventory', seller_id=current_user.id))
    return render_template('create_product.html', form=form, isseller=1, error=0)