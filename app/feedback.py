from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import jsonify


from .models.feedback import Feedback

from flask import Blueprint
bp = Blueprint('feedback', __name__)

@bp.route('/recent_feedback')
def recent_feedback():
    if current_user.is_authenticated:
        user_id = current_user.id
        feedbacks = Feedback.get_recent_feedback(user_id, 5)
    else:
        feedbacks=[]
    return render_template('recent_feedback.html', feedbacks=feedbacks)

@bp.route('/all_feedback')
def all_feedback():
    if current_user.is_authenticated:
        user_id = current_user.id
        full_feedback = Feedback.get_all_feedback(user_id)
    else:
        full_feedback=[]
    return render_template('all_feedback.html', full_feedback=full_feedback)

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                                             ('4', '4'), ('5', '5')],
                                              coerce = int, validators = [DataRequired()])
    comment = TextAreaField('Review', validators= [DataRequired()])
    submit = SubmitField('Submit feedback')

@bp.route('/post_feedback<int:pid>', methods=['GET', 'POST'])
def post_feedback(pid):
    if current_user.is_authenticated is False:
        return redirect(url_for('users.login'))
    user_id = current_user.id
    form = FeedbackForm()
    if form.validate_on_submit():
        time_posted = datetime.now()
        if Feedback.add_product_feedback(user_id, pid, form.rating.data, form.comment.data, time_posted):
            flash('Feedback successfully submitted!')
            return redirect(url_for('index.index'))
    return render_template('post_feedback.html', title='Submit feedback', form=form)