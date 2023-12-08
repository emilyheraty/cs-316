from flask import current_app as app



class Feedback():
    def __init__(self, id, user_id, pid, seller_id, review_type, rating, comment, time_posted):
        self.id = id
        self.user_id = user_id
        self.pid = pid
        self.seller_id = seller_id
        self.review_type = review_type
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
            seller_id = result[3],
            review_type = result[4],
            rating = result[5],
            comment = result[6],
            time_posted = result[7])
            feedbacks.append(feedback)
        
        return feedbacks


    @staticmethod
    def get_all_feedback(user_id):
        rows = app.db.execute("""
        SELECT * 
        FROM Feedback
        WHERE user_id = :user_id
        ORDER BY time_posted DESC
        """,
        user_id=user_id)
        
        return [Feedback(*row) for row in rows]
    
    @staticmethod
    def add_product_feedback(user_id, pid, seller_id, review_type, rating, comment, time_posted):
        feedbackCount = app.db.execute("""
        SELECT
        COUNT(*)
        FROM Feedback                             
        """)
        rows = app.db.execute("""
        INSERT INTO Feedback(id, user_id, pid, seller_id, review_type, rating, comment, time_posted)
        VALUES(:id, :user_id, :pid, :seller_id, :review_type, :rating, :comment, :time_posted)
        RETURNING id
                              """,
        id=feedbackCount[0][0], user_id = user_id, pid = pid, 
            seller_id = seller_id, review_type = review_type, rating = rating, comment = comment,
            time_posted = time_posted)
        return 1

    @staticmethod
    def edit_feedback(id, rating, comment, time_posted):
        new = app.db.execute("""
            UPDATE Feedback
            SET rating = :rating, comment = :comment, time_posted = :time_posted
            WHERE id = :id""", id = id, rating = rating, comment = comment, time_posted = time_posted)
        return new


    @staticmethod
    def get_partial_feedback(user_id, per_page, off):
        rows = app.db.execute("""
            SELECT p.rating, p.comment, p.time_posted, p.name, p.pid, p.id 
            FROM (
                              SELECT Feedback.id, Feedback.rating, Feedback.comment, Feedback.time_posted, Products.name, Feedback.pid
                              FROM Feedback 
                                    INNER JOIN Products ON Feedback.pid = Products.id
                              WHERE user_id = :user_id
                              ) as p
            ORDER BY time_posted DESC
            LIMIT :per_page
            OFFSET :off
                              """,
                              user_id = user_id, per_page = per_page, off = off)
        return rows
    
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
        SELECT DISTINCT Purchases.pid
        FROM Purchases, Feedback
        WHERE Purchases.uid = :uid 
        AND NOT EXISTS(
                              SELECT *
                              FROM Feedback, Purchases
                              WHERE Feedback.user_id = :uid AND Feedback.pid = Purchases.pid
        )
        """, uid = uid)
        return rows
    

    @staticmethod
    def get_seller(pid):
        rows = app.db.execute("""
        SELECT DISTINCT Sellers.id 
        FROM Sellers, Inventory, Products
        WHERE Products.id = :pid
        AND Products.name = Inventory.product_name
        AND Inventory.id = Sellers.id""", pid = pid)

        return int(rows[0][0])


    @staticmethod
    def get_partial_pending(uid, per_page, off):
        rows = app.db.execute("""
        SELECT DISTINCT Purchases.pid
        FROM Purchases, Feedback
        WHERE Purchases.uid = :uid
        AND NOT EXISTS(
                              SELECT *
                              FROM Feedback, Purchases
                              WHERE Feedback.user_id = :uid AND Feedback.pid = Purchases.pid
        )
        LIMIT :per_page
        OFFSET :off
        """, uid = uid, per_page = per_page, off = off)
        return rows
    
    @staticmethod
    def get_customer_feedback_seller(seller_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'seller'
                              """, seller_id=seller_id)
        return rows
    
    @staticmethod
    def get_customer_feedback_product(seller_id):
        rows = app.db.execute("""
            SELECT *
            FROM Feedback
            WHERE seller_id = :seller_id AND
            review_type = 'product' 
                              """, seller_id=seller_id)
        return rows


    @staticmethod
    def get_purchase_name_pending(uid):
        rows = app.db.execute("""
        SELECT DISTINCT Purchases.pid, Products.name
        FROM Purchases, Products, Feedback
        WHERE Purchases.uid = :uid AND
        Products.id = Purchases.pid AND
        Purchases.fulfillment_status = 1 
        
        
                """, uid = uid)
        return rows
    
    @staticmethod
    def get_purchase_name_posted(uid):
        rows = app.db.execute("""
                SELECT DISTINCT p.pid, p.name
                FROM (SELECT name, p2.id, pid, uid 
                    FROM Products as p1
                    INNER JOIN Purchases as p2 ON p2.pid = p1.id 
                    WHERE uid = :uid) as p
                """, uid = uid)
        return rows
 

