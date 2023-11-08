from flask import render_template
from flask_login import current_user
import datetime
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
    return render_template('recent_feedback.html', feedback=feedbacks)

@bp.route('/all_feedback')
def all_feedback():
    if current_user.is_authenticated:
        user_id = current_user.id
        full_feedback = Feedback.get_all_feedback(user_id)
    else:
        full_feedback=[]
    return render_template('all_feedback.html', feedback=full_feedback)