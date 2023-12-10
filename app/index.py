from flask import render_template
from flask import redirect, Blueprint, request, session, url_for
from flask_wtf import FlaskForm
from flask_login import current_user, login_required
import datetime
from .models.feedback import Feedback
from .models.product import Product
from .models.purchase import Purchase
from .models.inventory import Inventory
from flask import current_app, request
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter, get_page_args
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SearchField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
bp = Blueprint('index', __name__)

class SearchForm(FlaskForm):
    keyword = StringField('Find a product')
    submit = SubmitField('Search')

class FilterForm(FlaskForm):
    status = SelectField('Filter', choices=[('all', 'All'),
                        ('hoodies_sweatshirts', 'Hoodies & Sweatshirts'), 
                        ('pants', 'Pants'),
                        ('tees', 'Tees'),
                        ('shorts', 'Shorts'),
                        ('jackets', 'Jackets'),
                        ('bras_tanks', 'Bras & Tanks'),
                        ('tanks', 'Tanks'),
                        ('gear', 'Gear')])
    submit = SubmitField('Filter')

@bp.route('/', methods = ['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        is_seller = Inventory.isSeller(current_user.id)[0][0]
    else:
        is_seller = False

    # pagination
    per_page = 10
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    products_all = Product.get_all()
    search = False
    q = request.args.get('q')
    if q:
        search = True

    filterForm = FilterForm()
    if filterForm.is_submitted():
        if filterForm.status.data == 'hoodies_sweatshirts':
            str = "Hoodies"
        elif filterForm.status.data == 'pants':
            str = "Pants"
        elif filterForm.status.data == 'tees':
            str = "Tees"
        elif filterForm.status.data == 'shorts':
            str = "Shorts"
        elif filterForm.status.data == 'jackets':
            str = "Jackets"
        elif filterForm.status.data == 'bras_tanks':
            str = "Bras"
        elif filterForm.status.data == 'tanks':
            str = "Tanks"
        elif filterForm.status.data == 'gear':
            str = "Gear"
        else:
            return redirect(url_for('index.index'))

        print(str)
        products = Product.getOneCategory(str)
        print("Number of products in category: ", len(products))
        pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(products), search=search, record_name='products')
        return render_template('index.html', avail_products=products[offset: offset + per_page], isseller=is_seller, pagination=pagination, filterForm=filterForm)

        # pagination = Pagination(page=page, per_page=per_page, total=len(purchases))
        # return render_template('index.html',
        #                     purchases=purchases[offset: offset + per_page], pagination=pagination, isseller=isseller,
        #                     searchForm=searchForm, sortForm=sortForm, filterForm=filterForm)

    
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(products_all), search=search, record_name='products')

    # render the page by adding information to the index.html file
    return render_template('index.html', avail_products=products_all[offset: offset + per_page], isseller=is_seller, pagination=pagination, filterForm=filterForm)

