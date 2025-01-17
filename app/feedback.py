from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import jsonify
from flask_paginate import Pagination, get_page_parameter, get_page_args

from .models.inventory import Inventory
from .models.feedback import Feedback
from .models.purchase import Purchase
from .models.product import Product
from .models.inventory import Inventory
from .models.user import User

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


@bp.route('/customer_feedback<int:seller_id>')
def customer_feedback(seller_id):
    per_page = 4
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page

    if current_user.is_authenticated:
        user_id = current_user.id
        is_seller = Inventory.isSeller(current_user.id)[0][0]
        #if(Inventory.isSeller(seller_id)[0][0]):
        full_feedback_seller = Feedback.get_customer_feedback_seller(seller_id)
        partial_feedback_seller = Feedback.get_partial_customer_feedback_seller(seller_id, per_page, offset)
        full_feedback_product = Feedback.get_customer_feedback_product(seller_id)
        partial_feedback_product = Feedback.get_partial_customer_feedback_product(seller_id, per_page, offset)
        search = False
        q = request.args.get('q')
        if q:
            search = True
        
        search_2 = False
        q2 = request.args.get('q2')
        if q2:
            search_2 = True
    else:
        partial_feedback_seller = []
        partial_feedback_product = []
    pagination = Pagination(page=page, per_page=per_page, offset=offset, total=len(full_feedback_seller), 
                            search=search, record_name='seller reviews')
    pagination2 = Pagination(page=page, per_page=per_page, offset=offset, total=len(full_feedback_product), 
                              search=search_2, record_name='product reviews')
    
    return render_template('customer_feedback.html',partial_feedback_seller=partial_feedback_seller, 
                           partial_feedback_product=partial_feedback_product, pagination = pagination, pagination2 = pagination2, isseller=is_seller)


@bp.route('/all_feedback', methods=['GET'])
def all_feedback():
    search = False
    q = request.args.get('q')
    if q:
        search = True

    per_page = 4
    page1 = request.args.get(get_page_parameter(), type=int, default=1)
    offset1 = (page1 - 1) * per_page

    page2 = request.args.get(get_page_parameter(), type=int, default=1)
    offset2 = (page2 - 1) * per_page

    

    if current_user.is_authenticated:
        user_id = current_user.id
        is_seller = Inventory.isSeller(current_user.id)[0][0]
        full_feedback = Feedback.get_all_feedback(user_id)
        partial_feedback = Feedback.get_partial_feedback(user_id, per_page, offset1)
        pending = Feedback.pending_products(user_id)
        partial_pending = Feedback.get_partial_pending(user_id, per_page, offset2)
        purchase_name_pending = Feedback.get_purchase_name_pending(user_id)
        

        num = 0
        isseller = Inventory.isSeller(current_user.id)[0][0]
        names = []
        for feedback in full_feedback:
            if (feedback.review_type == 'seller'):
                seller_id = feedback.seller_id
                s1 = User.get_profile_info(seller_id).firstname
                s2 = User.get_profile_info(seller_id).lastname
                name = " ".join([s1, s2])
                names.append(name)
            if (feedback.review_type == 'product'):
                product_id = feedback.pid
                name = Product.get(product_id).name
                names.append(name)
        
       
    

    else:
        full_feedback=[]
        pending = []
    pagination = Pagination(page=page1, per_page=per_page, total=len(full_feedback), search = search, offset1 = offset1, record_name = 'product reviews')
    pagination_2 = Pagination(page=page2, per_page=per_page, total=len(purchase_name_pending), search = search, offset2 = offset2, record_name = 'purchases to review')
    
    return render_template('all_feedback.html', partial_feedback = partial_feedback, purchase_name_pending = purchase_name_pending, pagination = pagination, pending = pending, partial_pending = partial_pending, pagination_2 = pagination_2, names = names, isseller=is_seller)

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                                             ('4', '4'), ('5', '5')],
                                              coerce = int, validators = [DataRequired()])
    #review_type = SelectField('Review product or seller?', choices = [('product', 'product'), ('seller', 'seller')], validators = [DataRequired()])
    comment = TextAreaField('Review', validators= [DataRequired()])
    submit = SubmitField('Submit')
   



@bp.route('/post_feedback<int:pid>', methods=['GET', 'POST'])
def post_feedback(pid):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    else:
        is_seller = Inventory.isSeller(current_user.id)[0][0]

    user_id = current_user.id
    already_reviewed = (not(Feedback.check_past(pid, user_id)))
    seller_id = Feedback.get_seller(pid)[0][0]
    form = FeedbackForm()
    if form.is_submitted():
       # if(form.review_type.data == 'seller'):
         #   if(Feedback.seller_review_check(seller_id)):
         #       flash('Already reviewed seller')
          #      return redirect(url_for('feedback.all_feedback'))
        if Feedback.add_product_feedback(user_id, pid, seller_id, 'product', form.rating.data, form.comment.data, datetime.datetime.now()):
            #flash('Feedback successfully submitted!')
            return redirect(url_for('feedback.all_feedback'))
    return render_template('post_feedback.html', title='Submit', form=form, already_reviewed = already_reviewed, isseller=is_seller)


@bp.route('/post_feedback_seller<int:seller_id>', methods=['GET', 'POST'])
def post_feedback_seller(seller_id):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    else:
        is_seller = Inventory.isSeller(current_user.id)[0][0]
    
    user_id = current_user.id
    already_reviewed=(not( Feedback.check_past_seller(seller_id, user_id)))
    if(not( Feedback.check_purchased(seller_id, user_id))):
        return redirect(url_for('index.index'))
    form = FeedbackForm()
    if form.is_submitted():
       # if(form.review_type.data == 'seller'):
         #   if(Feedback.seller_review_check(seller_id)):
         #       flash('Already reviewed seller')
          #      return redirect(url_for('feedback.all_feedback'))
        if Feedback.add_product_feedback(user_id, None, seller_id, 'seller', form.rating.data, form.comment.data, datetime.datetime.now()):
            #flash('Feedback successfully submitted!')
            return redirect(url_for('feedback.all_feedback'))
    return render_template('post_feedback_seller.html', title='Submit', form=form, already_reviewed = already_reviewed, isseller=is_seller)


class FeedbackEditForm(FlaskForm):
    rating = SelectField('New Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                                             ('4', '4'), ('5', '5')],
                                              coerce = int, validators = [DataRequired()])
    comment = TextAreaField('New Review', validators= [DataRequired()])
    submit = SubmitField('Submit Edits')

@bp.route('/edit_feedback<int:id>', methods=['GET', 'POST'])
def edit_feedback(id):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    else:
        is_seller = Inventory.isSeller(current_user.id)[0][0]

    form = FeedbackEditForm()
    if form.is_submitted():
        if Feedback.edit_feedback(id, form.rating.data, form.comment.data, datetime.datetime.now()):
            #flash('Feedback successfully edited!')
            return redirect(url_for('feedback.all_feedback'))
    return render_template('edit_feedback.html', title='Submit', form=form, isseller=is_seller)


class FeedbackDeleteForm(FlaskForm):
    submit = SubmitField('Delete')

@bp.route('/delete_feedback<int:id>', methods=['GET', 'POST'])
def delete_feedback(id):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    else:
        is_seller = Inventory.isSeller(current_user.id)[0][0]
    review = Feedback.get_feedback_info(id)
    form = FeedbackDeleteForm()
    if form.is_submitted():
        if Feedback.delete_feedback(id):
            #flash('Feedback successfully deleted.')
            return redirect(url_for('feedback.all_feedback'))
    return render_template('delete_feedback.html', review = review, title = 'Delete', form = form, isseller=is_seller)
    
