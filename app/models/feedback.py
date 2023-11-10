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
        

    @staticmethod
    def get_partial_feedback(user_id, per_page, off):
        rows = app.db.execute("""
            SELECT * 
            FROM Feedback
            WHERE user_id = :user_id
            ORDER BY time_posted DESC
            LIMIT :per_page
            OFFSET :off
                              """,
                              user_id = user_id, per_page = per_page, off = off)
        return [Feedback(*row) for row in rows]
   # @staticmethod
   # def get(id):
   #     rows = app.db.execute("""
   #         SELECT id, pid, rating
   #         FROM Feedback
   #         WHERE id = :id
   #         """, id = id)
   #     return Feedback(*(rows[0])) if rows else None
    
    @staticmethod
    def pending_products(uid):
        rows = app.db.execute("""
        SELECT DISTINCT pid
        FROM Purchases
        WHERE uid = :uid
        """, uid = uid)
        return rows
    
    @staticmethod
    def get_partial_pending(uid, per_page, off):
        rows = app.db.execute("""
        SELECT DISTINCT pid
        FROM Purchases
        WHERE uid = :uid
        LIMIT :per_page
        OFFSET :off
        """, uid = uid, per_page = per_page, off = off)
        return rows
    
    @staticmethod
    def get_purchase_name(uid):
        
        rows = app.db.execute("""
                SELECT DISTINCT p.pid, p.name
                FROM (SELECT name, p2.id, pid, uid 
                    FROM Products as p1
                    INNER JOIN Purchases as p2 ON p2.pid = p1.id 
                    WHERE uid = :uid) as p""", uid = uid)
        return rows
 

