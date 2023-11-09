from flask import current_app as app



class Feedback():
    def __init__(self, id, user_id, pid, rating, comment, time_posted):
        self.id = id
        self.user_id = user_id
        self.pid = pid
        self.rating = rating
        self.comment = comment
        self.time_posted = time_posted

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
            feedback = Feedback(
            id = result[0],
            user_id = result[1],
            pid = result[2],
            rating = result[3],
            comment = result[4],
            time_posted = result[5])
            feedbacks.append(feedback)
        
        return feedbacks

    @staticmethod
    def get_all_feedback(user_id):
        rows = app.db.execute("""
        SELECT * FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        """,
        user_id=user_id)
        
        return [Feedback(*row) for row in rows]
    
    def add_product_feedback(user_id, pid, rating, comment, time_posted):
        rows = app.db.execute("""
            INSERT INTO Feedback(user_id, pid, rating, comment, time_posted)
            VALUES(:user_id, :pid, :rating, :comment, :time_posted)
            RETURNING id
            """,
            user_id = user_id, pid = pid, rating = rating, comment = comment,
            time_posted = time_posted)
        return 1
    
   # @staticmethod
   # def get(id):
   #     rows = app.db.execute("""
   #         SELECT id, pid, rating
   #         FROM Feedback
   #         WHERE id = :id
   #         """, id = id)
   #     return Feedback(*(rows[0])) if rows else None
    
    @staticmethod
    def pending_products(user_id):
        rows = app.db.execute("""
        SELECT DISTINCT pid
        FROM Purchases
        WHERE uid = :user_id
        """, user_id = user_id)
        return rows
    
    @staticmethod
    def get_purchase_name(user_id):
        rows = app.db.execute("""
            SELECT name
            FROM Products, Purchases
            WHERE Purchases.uid = :user_id
                and Purchases.id = Products.id""", user_id = user_id)
        return rows
    

