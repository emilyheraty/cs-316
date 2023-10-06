from flask import Blueprint, request, jsonify
from app.models import feedback
from app import db
from flask import render_template
from flask_login import login_required
from flask import current_app

bp = Blueprint('feedback', __name__)


@bp.route('/recent_feedback')
@login_required
def recent_feedback():
    user_id = 0
    feedbacks = feedback.get_recent_feedback(current_app.db, user_id)
    return render_template('recent_feedback.html', feedbacks=feedbacks)