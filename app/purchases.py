from flask import render_template, redirect, Blueprint, request, session, url_for
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from .models.order import Order
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.product import Product
from flask_paginate import Pagination, get_page_parameter
from flask import Blueprint
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SearchField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo


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

class UpdateFulfillmentStatus(FlaskForm):
    time = DateTimeField('Order Time')
    buyer = IntegerField('Buyer ID')
    status = BooleanField('Fulfilled?')
    submit = SubmitField('Submit')

class SearchOrders(FlaskForm):
    keyword = StringField('Find a product ordered')
    submit = SubmitField('Search')


class FilterOrders(FlaskForm):
    status = SelectField('Filter', choices=[('all', 'All'), ('fulfilled', 'Fulfilled'), ('not_fulfilled', 'Not Fulfilled')])
    submit = SubmitField('Filter')


@bp.route('/orders/', methods=['GET', 'POST'])
def orders():
    if current_user.is_authenticated and Inventory.isSeller(current_user.id)[0][0]:
        isseller = Inventory.isSeller(current_user.id)[0][0]

        searchForm = SearchOrders()
        filterForm = FilterOrders()
        form_fulfilled = UpdateFulfillmentStatus()

        # Move per_page definition to a position before it's used
        per_page = 8
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page
        search = request.args.get('q')

        # Use the correct method to get partial orders (assuming such a method exists)
        lineitems = Order.getOrdersBySellerId(current_user.id)
        lineitems_partial = Order.getPartialOrdersBySellerId(current_user.id, per_page, offset)
        print("orders original:", lineitems_partial)
        
        pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(lineitems_partial), search=search, record_name='lineitems')
        print("GETTING HERE")

        if form_fulfilled.is_submitted():
            lineitems_partial = Order.getPartialOrdersBySellerId(current_user.id, per_page, offset)
            print("WHY IS IT NOT WORKING")
            order_time = form_fulfilled.time.data
            bid = form_fulfilled.buyer.data
            fulfilled = form_fulfilled.status.data
            print("fulfilled?: ", fulfilled)
            result = Order.updateFulfillmentStatus(current_user.id, order_time, bid, fulfilled)
            print("WHAT")
            if result == 0:
                return render_template('orders.html', 
                                        items=lineitems_partial, 
                                        pagination=pagination, 
                                        isseller=isseller,
                                        form_fulfilled=form_fulfilled,
                                        searchForm=searchForm,
                                        filterForm=filterForm)
            return redirect(url_for('purchases.orders'))
        else:
            print("Fulfillment Form validation failed:", form_fulfilled.errors)

        # if searchForm.is_submitted():
        #     print("HELLO?")
        #     str = searchForm.keyword.data
        #     orders = Order.searchProductName(current_user.id, str, per_page, offset)
        #     print("GET ANY ORDERS BACK?: ", orders)
        #     pagination = Pagination(page=page, per_page=per_page, total=len(orders))
        #     return render_template('orders.html', 
        #                                 items=orders, 
        #                                 pagination=pagination, 
        #                                 isseller=isseller,
        #                                 form_fulfilled=form_fulfilled,
        #                                 searchForm=searchForm,
        #                                 filterForm=filterForm)
        # else:
        #     print("search form data: ", request.form)
        #     print("Search Form validation failed: ", searchForm.errors)
    

        # if filterForm.is_submitted():
        #     if filterForm.status.data == 'fulfilled':
        #         status = True
        #     elif filterForm.status.data == 'not_fulfilled':
        #         status = False
        #     else:
        #         return redirect(url_for('purchases.orders'))
        #     print("status: ", status)
        #     orders = Order.getOrdersByStatus(status, current_user.id, per_page, offset)
        #     pagination = Pagination(page=page, per_page=per_page, total=len(orders))
        #     return render_template('orders.html', 
        #                                 items=orders, 
        #                                 pagination=pagination, 
        #                                 isseller=isseller,
        #                                 form_fulfilled=form_fulfilled,
        #                                 searchForm=searchForm,
        #                                 filterForm=filterForm)

        return render_template('orders.html', items=lineitems_partial, pagination=pagination, isseller=isseller, form_fulfilled=form_fulfilled,searchForm=searchForm, filterForm=filterForm)

        
    else:
        lineitems = []
        isseller = 0
        # Move per_page definition to a position before it's used
        per_page = 8
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page
        search = request.args.get('q')
        pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(lineitems), search=search, record_name='lineitems')
        return render_template('orders.html', items=lineitems, pagination=pagination, isseller=isseller, form_fulfilled=form_fulfilled,searchForm=searchForm, filterForm=filterForm)
