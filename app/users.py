from flask import render_template, redirect, url_for, flash, request
from flask_paginate import Pagination, get_page_args
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp

from .models.user import User
from .models.inventory import Inventory
from .models.feedback import Feedback
from .models.product import Product


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    balance = DecimalField('Balance', places=2, validators=[DataRequired()])
    is_seller = BooleanField('Check if you want to be a seller')
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data,
                         form.balance.data,
                         form.is_seller.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))


@bp.route('/account', methods=['GET'])
def account():
    if current_user.is_authenticated is False:
        isseller = 0
        return redirect(url_for('users.login'))
    else:
        isseller = Inventory.isSeller(current_user.id)[0][0]
    return render_template('account.html', isseller=isseller)


@bp.route('/account/profile', methods=['GET'])
def profile():
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    user = User.get_profile_info(current_user.id)
    return render_template('profile.html', user=user)


class EditForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    balance = DecimalField('Balance', places=2, validators=[DataRequired()])
    is_seller = BooleanField('Check if you want to be a seller')
    save = SubmitField('Save')
    cancel = SubmitField('Cancel')

    def validate_email(self, email):
        if User.email_exists(email.data) and current_user.email != email.data:
            raise ValidationError('Already a user with this email.')


class EditPasswordForm(FlaskForm):
    currentpassword = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(),
                                       EqualTo('password')])
    save = SubmitField('Save')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})


@bp.route('/account/profile/edit', methods=['GET', 'POST'])
def edit():
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    user = User.get_profile_info(current_user.id)
    form = EditForm(obj=user)
    if (form.validate_on_submit):
        if (form.save.data):
            if User.update_info(current_user.id,
                                form.email.data,
                                form.firstname.data,
                                form.lastname.data,
                                form.address.data,
                                form.balance.data,
                                form.is_seller.data):
                    flash('Profile changes have been saved')
                    return redirect(url_for('users.profile'))
        elif(form.cancel.data):
            return redirect(url_for('users.profile'))
    return render_template('edit.html', form=form, user=user)


@bp.route('/account/profile/changepassword', methods=['GET', 'POST'])
def changepassword():
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    form = EditPasswordForm()
    if(form.cancel.data):
        return redirect(url_for('users.profile'))
    if form.validate_on_submit():
        user = User.get_by_auth(current_user.email, form.currentpassword.data)
        if user is None:
            flash('Invalid current password')
            return redirect(url_for('users.changepassword'))
        if User.update_password(current_user.id, form.password.data):
            flash('Password successfully changed')
            return redirect(url_for('users.profile'))
    return render_template('changepassword.html', form=form)


@bp.route('/seller/<int:seller_id>', methods=['GET'])
def seller_public_profile(seller_id):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    user_id = current_user.id
    can_review = Feedback.check_purchased(seller_id, user_id)
    seller = User.get_profile_info(seller_id)
    if(seller.is_seller):
        seller_inventory = Inventory.getInventory(seller_id)
        seller_products = []
        for item in seller_inventory:
            product = Product.get_product_by_name(item.product_name)
            seller_products.append(product)
            
        seller_feedback = Feedback.get_recent_customer_feedback_seller(seller_id, 5)

        avg_rating = Feedback.avg_rating_seller(seller_id)[0][0]
        if avg_rating is not None:
            avg_rating = round(avg_rating, 2)
        has_rating = avg_rating is not None
        num_rating = Feedback.num_rating_seller(seller_id)[0][0]
        

        page1, per_page1, offset1 = get_page_args(page_parameter='page1', per_page_parameter='per_page1')
        page2, per_page2, offset2 = get_page_args(page_parameter='page2', per_page_parameter='per_page2')

        products = seller_products[offset1: offset1 + per_page1]
        feedback = seller_feedback[offset2: offset2 + per_page2]
        pagination_products = Pagination(page=page1, per_page=per_page1, search=search, total=len(seller_products), href='/seller/0?page1={0}')
        pagination_feedback = Pagination(page=page2, per_page=per_page2, total=len(seller_feedback), href='/seller/0?page2={0}')

        return render_template('seller_profile.html', seller=seller, seller_products=products, seller_feedback=feedback,
                                pagination_products=pagination_products, pagination_feedback=pagination_feedback, can_review = can_review, 
                                avg_rating = avg_rating, has_rating = has_rating, num_rating = num_rating)
    else:
        return render_template('seller_profile.html', seller=seller)

@bp.route('/seller_/<int:pid>', methods=['GET'])
def seller_public_profile_by_pid(pid):
    cid = Product.get_cid_by_pid(pid)
    return redirect(url_for('users.seller_public_profile', seller_id=cid))
