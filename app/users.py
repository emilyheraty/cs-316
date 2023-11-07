from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User


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
        return redirect(url_for('users.login'))
    return render_template('account.html')

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




    
