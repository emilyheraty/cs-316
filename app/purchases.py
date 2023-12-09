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

@bp.route('/purchases', methods = ['GET', 'POST'])
def purchases():
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid(
            current_user.id)
        products = []
        for purchase in purchases:
            products.append(Product.get(purchase.pid)) 

        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        purchases = None
        products = None
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
        products = []
        for purchase in purchases:
            products.append(Product.get(purchase.pid))
        pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchase_history=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            products=products[offset: offset + per_page],
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    
    if sortForm.is_submitted():
        if sortForm.sort.data == 'amount_asce':
            purchases = Purchase.get_by_ascending_amount(current_user.id)
            products = []
            for purchase in purchases:
                products.append(Product.get(purchase.pid))
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        elif sortForm.sort.data == 'amount_desc':
            purchases = Purchase.get_by_descending_amount(current_user.id)
            products = []
            for purchase in purchases:
                products.append(Product.get(purchase.pid))
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        elif sortForm.sort.data == 'time_natural':
            purchases = Purchase.get_by_natural_time(current_user.id)
            products = []
            for purchase in purchases:
                products.append(Product.get(purchase.pid))
            pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        
        return render_template('purchases.html',
                            purchase_history=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            products=products[offset: offset + per_page],
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    

    if searchForm.is_submitted():
        purchases = Purchase.get_by_product_name(searchForm.keyword.data, current_user.id)
        products = []
        for purchase in purchases:
            products.append(Product.get(purchase.pid))
        pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        return render_template('purchases.html',
                            purchase_history=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            products=products[offset: offset + per_page],
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)
    

    return render_template('purchases.html',
                            purchase_history=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
                            products=products[offset: offset + per_page],
                            searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)


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
            states.append(state[0])
            product_count.append(state[1])

    

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
    productForm.product.choices = ["All Products"] + [(a[1], a[1]) for a in Inventory.getInventory(current_user.id)]

    if productForm.product.data != ("None" or "All Products"):
        product_by_state = Purchase.get_all_by_state_product(current_user.id, productForm.product.data)
        states = []
        product_count = []
        for product in product_by_state:
            states.append(product[0])
            product_count.append(int(product[1]))
        return render_template('statistics.html', isseller=isseller, top_products=top_products, count=count, 
                                available_years=availableYears, total_amount=total_amount, spendingForm=spendingForm, productForm=productForm,
                                states=states, product_count=product_count, product=productForm.product.data)

        

    if spendingForm.years.data != ("All Years" or "None"):
        grouped_data_m = Purchase.get_by_year(current_user.id, spendingForm.years.data)
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
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
                            available_years=availableYears, total_amount=total_amount, spendingForm=spendingForm,
                              states=states, product_count=product_count, product=productForm.product.data)
