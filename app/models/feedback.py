from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import desc
from flask import current_app as app

Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'Feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Users.id'))
    product_id = Column(Integer, ForeignKey('Products.id'))
    rating = Column(Integer)
    comment = Column(Text)
    time_posted = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def get_recent_feedback(user_id, limit):

        sql = """
        SELECT * FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        LIMIT :limit
        """
        results = app.db.execute(sql, user_id=user_id, limit=limit)
        
        feedbacks = []
        for result in results:
            feedback = Feedback()
            feedback.id = result[0]
            feedback.user_id = result[1]
            feedback.product_id = result[2]
            feedback.rating = result[3]
            feedback.comment = result[4]
            feedback.time_posted = result[5]
            feedbacks.append(feedback)
        
        return feedbacks

    @staticmethod
    def get_full_feedback(user_id):
        sql = """
        SELECT * FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        """

        full_results = app.db.execute(sql, user_id=user_id)
        full_feedback = []
        for result in full_results:
            feedback = Feedback()
            feedback.id = full_results[0]
            feedback.user_id = full_results[1]
            feedback.product_id = full_results[2]
            feedback.rating = full_results[3]
            feedback.comment = full_results[4]
            feedback.time_posted = full_results[5]
            full_feedback.append(feedback)
        
        return full_feedback