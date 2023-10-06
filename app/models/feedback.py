from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import desc

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
    def get_recent_feedback(cls, db, user_id, limit=5):

        sql = """
        SELECT * FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        LIMIT :limit
        """
        results = db.execute(sql, user_id=user_id, limit=limit)
        
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