from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import jsonify
from flask_paginate import Pagination, get_page_parameter

from .models.inventory import Inventory
from .models.feedback import Feedback
from .models.purchase import Purchase
from .models.product import Product

from flask import Blueprint
bp = Blueprint('feedback', __name__)

@bp.route('/recent_feedback')
def recent_feedback():
    if current_user.is_authenticated:
        user_id = current_user.id
        feedbacks = Feedback.get_recent_feedback(user_id, 5)
        isseller = Inventory.isSeller(current_user.id)[0][0]
    else:
        feedbacks=[]
        isseller=0
    return render_template('recent_feedback.html', feedbacks=feedbacks, isseller=isseller)

@bp.route('/all_feedback')
def all_feedback():
    per_page = 4
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    if current_user.is_authenticated:
        user_id = current_user.id
        full_feedback = Feedback.get_all_feedback(user_id)
        partial_feedback = Feedback.get_partial_feedback(user_id, per_page, offset)
        pending = Feedback.pending_products(user_id)
        partial_pending = Feedback.get_partial_pending(user_id, per_page, offset)
        purchase_name = Feedback.get_purchase_name(user_id)
        num = 0
        isseller = Inventory.isSeller(current_user.id)[0][0]
        search = False
        q = request.args.get('q')
        if q:
            search = True
    else:
        full_feedback=[]
        pending = []
        isseller=0
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(full_feedback), search=search, record_name='feedback')
    pagination_2 = Pagination(page=page, per_page=per_page, offset=offset, total=len(purchase_name), search=search, record_name='pending')
    return render_template('all_feedback.html', partial_feedback = partial_feedback, purchase_name = purchase_name, pagination = pagination, pending = pending, partial_pending = partial_pending, pagination_2 = pagination_2, isseller=isseller)

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                                             ('4', '4'), ('5', '5')],
                                              coerce = int, validators = [DataRequired()])
    comment = TextAreaField('Review', validators= [DataRequired()])
    submit = SubmitField('Submit')

@bp.route('/post_feedback<int:pid>', methods=['GET', 'POST'])
def post_feedback(pid):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
        
    user_id = current_user.id
    
    form = FeedbackForm()
    if form.is_submitted():
        if Feedback.add_product_feedback(user_id, pid, form.rating.data, form.comment.data, datetime.datetime.now()):
            flash('Feedback successfully submitted!')
            return redirect(url_for('feedback.all_feedback'))
    return render_template('post_feedback.html', title='Submit', form=form)

