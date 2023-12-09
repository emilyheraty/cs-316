from flask import render_template, redirect, Blueprint, request, session, url_for
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from wtforms import StringField, SubmitField, SelectField
from .models.order import Order
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.product import Product
from flask_paginate import Pagination, get_page_parameter
from flask import Blueprint

bp = Blueprint('purchases', __name__)


class SearchForm(FlaskForm):
    keyword = StringField('Find a product')
    submit = SubmitField('Search')

class SortForm(FlaskForm):
    sort = SelectField('Sort', choices=[('time_reverse', 'Time Purchased: Newest to Oldest'),
                                        ('time_natural', 'Time Purchased: Oldest to Newest'), 
                                        ('amount_asce', 'Total Amount: Low to High'), 
                                        ('amount_desc', 'Total Amount: High to Low')])
    submit = SubmitField('Sort')

class FilterForm(FlaskForm):
    status = SelectField('Filter', choices=[('all', 'All'), ('fulfilled', 'Fulfilled'), ('not_fulfilled', 'Not Fulfilled')])
    submit = SubmitField('Filter')

# buyers perspective
@bp.route('/purchases', methods = ['GET', 'POST'])
def purchases():
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(current_user.id)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        purchases = []
        isseller = 0

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination = Pagination(page=page, per_page=per_page, total=len(purchases))


    sortForm = SortForm()
    searchForm = SearchForm()
    filterForm = FilterForm()
    
    if filterForm.is_submitted():
        if filterForm.status.data == 'fulfilled':
            status = 1
        elif filterForm.status.data == 'not_fulfilled':
            status = 0
        else:
            return redirect(url_for('purchases.purchases'))
        purchases = Purchase.get_by_status(status, current_user.id)
        pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    if sortForm.is_submitted():
        if sortForm.sort.data == 'amount_asce':
            purchases = Purchase.get_by_ascending_amount(current_user.id)
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        elif sortForm.sort.data == 'amount_desc':
            purchases = Purchase.get_by_descending_amount(current_user.id)
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        elif sortForm.sort.data == 'time_natural':
            purchases = Purchase.get_by_natural_time(current_user.id)
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    
    if searchForm.is_submitted():
        purchases = Purchase.get_by_product_name(searchForm.keyword.data, current_user.id)
        pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    return render_template('purchases.html',
                        purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                        searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)

# sellers perspective
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
