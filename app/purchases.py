from flask import render_template, redirect, Blueprint, request, session, url_for
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import null
from .models.order import Order
from .models.purchase import Purchase
from .models.inventory import Inventory
from .models.product import Product
from flask_paginate import Pagination, get_page_parameter
from flask import Blueprint
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SearchField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import datetime

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
    
    if filterForm.validate_on_submit():
        if filterForm.status.data == 'fulfilled':
            status = True
        elif filterForm.status.data == 'not_fulfilled':
            status = False
        else:
            return redirect(url_for('purchases.purchases'))
        purchases = Purchase.get_by_status(status, current_user.id)
        pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
                            
    if sortForm.validate_on_submit():
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
    
    if searchForm.validate_on_submit():
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
            status = form_fulfilled.status.data
            if status:
                fulfilled_time = datetime.datetime.now()
            else:
                fulfilled_time = None
            print("fulfilled?: ", fulfilled_time)
            result = Order.updateFulfillmentStatus(current_user.id, order_time, bid, fulfilled_time)
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

        if searchForm.is_submitted():
            print("HELLO?")
            str = searchForm.keyword.data
            orders = Order.searchProductName(current_user.id, str, per_page, offset)
            print("GET ANY ORDERS BACK?: ", orders)
            pagination = Pagination(page=page, per_page=per_page, total=len(orders))
            return render_template('orders.html', 
                                        items=orders, 
                                        pagination=pagination, 
                                        isseller=isseller,
                                        form_fulfilled=form_fulfilled,
                                        searchForm=searchForm,
                                        filterForm=filterForm)
        else:
            print("search form data: ", request.form)
            print("Search Form validation failed: ", searchForm.errors)
    

        if filterForm.is_submitted():
            if filterForm.status.data == 'fulfilled':
                status = True
            elif filterForm.status.data == 'not_fulfilled':
                status = False
            else:
                return redirect(url_for('purchases.orders'))
            print("status: ", status)
            orders = Order.getOrdersByStatus(status, current_user.id, per_page, offset)
            pagination = Pagination(page=page, per_page=per_page, total=len(orders))
            return render_template('orders.html', 
                                        items=orders, 
                                        pagination=pagination, 
                                        isseller=isseller,
                                        form_fulfilled=form_fulfilled,
                                        searchForm=searchForm,
                                        filterForm=filterForm)

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

class SpendingForm(FlaskForm):
    years = SelectField("Year")
    submit = SubmitField("View")

class ProductForm(FlaskForm):
    product = SelectField("Product")
    submit = SubmitField("View")

@bp.route('/purchases/statistics', methods = ['GET', 'POST'])
def statistics():
    if current_user.is_authenticated:
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        isseller = 0

    states = []
    product_count = []
    if isseller == 1:
        seller_by_state = Purchase.get_all_by_state(current_user.id)
        for state in seller_by_state:
            if str(state[0]) != '':
                states.append(str(state[0]))
                product_count.append(str(state[1]))


    grouped_products = Purchase.get_by_product_count(current_user.id)
    top_products = []
    count = []
    for product in grouped_products:
        top_products.append(str(product[0]))
        count.append(int(product[1]))

    
    grouped_data = Purchase.get_all_years(current_user.id)
    selectedYears = ["All Years"]
    availableYears = []
    total_amount = []
    for purchase in grouped_data:
        selectedYears.append(int(purchase[0]))
        availableYears.append(int(purchase[0]))
        total_amount.append(int(purchase[1]))

    spendingForm = SpendingForm()
    spendingForm.years.choices = [(str(a), str(a)) for a in selectedYears]

    productForm = ProductForm()

    productForm.product.choices = ["All Categories"] + [(str(a[1])) for a in Inventory.getByCategory(current_user.id)]
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    if (productForm.validate_on_submit() and productForm.product.data != "None" and productForm.product.data != "All Categories"):
        product_by_state = Purchase.get_all_by_state_category(current_user.id, productForm.product.data)
        states = []
        product_count = []
        for product in product_by_state:
            states.append(product[0])
            product_count.append(int(product[1]))
        return render_template('statistics.html', isseller=isseller, top_products=top_products, count=count, 
                                available_years=availableYears, total_amount=total_amount, spendingForm=spendingForm, productForm=productForm,
                                states=states, product_count=product_count, product=productForm.product.data, year=spendingForm.years.data, months=months)
    
    
    if (spendingForm.validate_on_submit() and spendingForm.years.data != "All Years" and spendingForm.years.data != "None"):
        grouped_data_m = Purchase.get_by_year(current_user.id, spendingForm.years.data)
        months_data = []
        total_amount = []
        for purchase in grouped_data_m:
            months_data.append(months[int(purchase[0]) - 1])
            total_amount.append(int(purchase[1]))
        return render_template('statistics.html', isseller=isseller, top_products=top_products, count=count, 
                                available_years=availableYears, year=spendingForm.years.data, total_amount=total_amount,
                                spendingForm=spendingForm, productForm=productForm, months=months_data, states=states,
                                product_count=product_count, product=productForm.product.data)


    
    return render_template('statistics.html', isseller=isseller, top_products=top_products, count=count, 
                            available_years=availableYears, total_amount=total_amount, spendingForm=spendingForm, productForm=productForm,
                              states=states, product_count=product_count, product=productForm.product.data, year=spendingForm.years.data, months=[])

